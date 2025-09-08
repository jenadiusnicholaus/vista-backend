"""
Payment utility functions for Azam Pay integration
"""
import logging
import re
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from .azam_pay_checkout import AzamPayCheckout
from .azam_res_models import PaymentProvider, PaymentStatus, TransactionResponse
from .models import (
    MyBooking, MyBookingPayment, MyBookingPaymentStatus, MyBookingStatus,
    MyRenting, MyRentingPayment, MyRentingPaymentStatus, MyRentingStatus
)

logger = logging.getLogger(__name__)


class PaymentValidator:
    """Utility class for payment validation"""
    
    @staticmethod
    def validate_phone_number(phone_number: str, provider: str = None) -> Tuple[bool, str]:
        """
        Validate phone number format for Tanzanian mobile networks
        
        Args:
            phone_number: Phone number to validate
            provider: Specific provider to validate against (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not phone_number:
            return False, "Phone number is required"
        
        # Remove any spaces or special characters
        clean_number = re.sub(r'[^\d]', '', str(phone_number))
        
        # Check if it's 10 digits starting with 0
        if not re.match(r'^0\d{9}$', clean_number):
            return False, "Phone number must be 10 digits starting with 0"
        
        # Provider-specific validation
        provider_patterns = {
            'AIRTEL': [r'^0(78|68|75)\d{7}$'],
            'TIGO': [r'^0(71|65|67)\d{7}$'],
            'HALOPESA': [r'^0(62|76)\d{7}$'],
            'AZAMPESA': [r'^0(71|65|67|78|68|75|62|76)\d{7}$'],
            'MPESA': [r'^0(74|76)\d{7}$']
        }
        
        if provider:
            patterns = provider_patterns.get(provider.upper(), [])
            if not any(re.match(pattern, clean_number) for pattern in patterns):
                return False, f"Phone number {clean_number} is not valid for {provider} network"
        else:
            # Check against all patterns
            all_patterns = []
            for patterns in provider_patterns.values():
                all_patterns.extend(patterns)
            
            if not any(re.match(pattern, clean_number) for pattern in all_patterns):
                return False, "Phone number is not valid for any supported network"
        
        return True, ""
    
    @staticmethod
    def validate_amount(amount: Any) -> Tuple[bool, str, Optional[float]]:
        """
        Validate payment amount
        
        Args:
            amount: Amount to validate
            
        Returns:
            Tuple of (is_valid, error_message, validated_amount)
        """
        try:
            validated_amount = float(amount)
            
            if validated_amount <= 0:
                return False, "Amount must be positive", None
            
            if validated_amount > 5000000:  # 5 million TZS limit per Azam Pay spec
                return False, "Amount exceeds maximum limit of 5,000,000 TZS", None
            
            if validated_amount < 100:  # Minimum 100 TZS
                return False, "Amount must be at least 100 TZS", None
            
            return True, "", validated_amount
            
        except (ValueError, TypeError):
            return False, "Invalid amount format", None
    
    @staticmethod
    def validate_provider(provider: str) -> Tuple[bool, str]:
        """
        Validate payment provider
        
        Args:
            provider: Provider to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not provider:
            return False, "Payment provider is required"
        
        if not PaymentProvider.is_valid_provider(provider):
            valid_providers = PaymentProvider.get_all_providers()
            return False, f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
        
        return True, ""


class PaymentProcessor:
    """Main payment processing utility"""
    
    def __init__(self, user, booking_id: str = None, renting_id: str = None):
        """
        Initialize payment processor
        
        Args:
            user: Django user object
            booking_id: Booking ID for booking payments
            renting_id: Renting ID for renting payments
        """
        self.user = user
        self.booking_id = booking_id
        self.renting_id = renting_id
        self.logger = logging.getLogger(__name__)
        
        if booking_id and renting_id:
            raise ValueError("Cannot process both booking and renting payment simultaneously")
        
        if not booking_id and not renting_id:
            raise ValueError("Either booking_id or renting_id must be provided")
    
    def validate_payment_request(self, payment_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate payment request data
        
        Args:
            payment_data: Dictionary containing payment information
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['payment_method', 'accountNumber', 'amount']
        missing_fields = [field for field in required_fields if not payment_data.get(field)]
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Validate provider
        is_valid, error = PaymentValidator.validate_provider(payment_data['payment_method'])
        if not is_valid:
            return False, error
        
        # Validate phone number
        is_valid, error = PaymentValidator.validate_phone_number(
            payment_data['accountNumber'], 
            payment_data['payment_method']
        )
        if not is_valid:
            return False, error
        
        # Validate amount
        is_valid, error, _ = PaymentValidator.validate_amount(payment_data['amount'])
        if not is_valid:
            return False, error
        
        # Validate booking/renting exists and belongs to user
        if self.booking_id:
            try:
                MyBooking.objects.get(id=self.booking_id, user=self.user)
            except MyBooking.DoesNotExist:
                return False, "Booking not found or access denied"
        
        if self.renting_id:
            try:
                MyRenting.objects.get(id=self.renting_id, user=self.user)
            except MyRenting.DoesNotExist:
                return False, "Renting not found or access denied"
        
        return True, ""
    
    def process_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process payment request
        
        Args:
            payment_data: Payment information
            
        Returns:
            Dictionary with payment result
        """
        try:
            # Validate request
            is_valid, error_message = self.validate_payment_request(payment_data)
            if not is_valid:
                return {
                    'success': False,
                    'message': error_message
                }
            
            # Initialize Azam Pay checkout
            external_id = self.booking_id or self.renting_id
            azmpay = AzamPayCheckout(
                accountNumber=payment_data['accountNumber'],
                amount=float(payment_data['amount']),
                externalId=external_id,
                provider=payment_data['payment_method'].upper()
            )
            
            # Process payment
            response = azmpay.initCheckout()
            
            if not isinstance(response, dict):
                return {
                    'success': False,
                    'message': 'Invalid response from payment gateway'
                }
            
            if not response.get('success', False):
                return {
                    'success': False,
                    'message': response.get('message', 'Payment failed')
                }
            
            transaction_id = response.get('transactionId')
            if not transaction_id:
                return {
                    'success': False,
                    'message': 'No transaction ID received'
                }
            
            # Save payment record
            if self.booking_id:
                payment_record = self._save_booking_payment(payment_data, transaction_id)
            else:
                payment_record = self._save_renting_payment(payment_data, transaction_id)
            
            self.logger.info(f"Payment processed successfully: {transaction_id}")
            
            return {
                'success': True,
                'message': 'Payment initiated successfully',
                'transaction_id': transaction_id,
                'payment_id': payment_record.id if payment_record else None
            }
            
        except Exception as e:
            self.logger.error(f"Payment processing error: {str(e)}")
            return {
                'success': False,
                'message': 'Payment processing failed'
            }
    
    @transaction.atomic
    def _save_booking_payment(self, payment_data: Dict[str, Any], transaction_id: str):
        """Save booking payment record with atomic transaction"""
        from .booking_serializers import MyBookingPaymentSerializers, MyBookingPaymentStatusSerializers, MyBookingStatusSerializers
        
        try:
            # Save payment
            payment_serializer = MyBookingPaymentSerializers(data={
                'booking': self.booking_id,
                'user': self.user.id,
                'payment_method': payment_data['payment_method'],
                'transaction_id': transaction_id
            })
            
            if not payment_serializer.is_valid():
                self.logger.error(f"Payment serializer errors: {payment_serializer.errors}")
                return None
                
            payment_record = payment_serializer.save()
            
            # Save payment status
            payment_status_serializer = MyBookingPaymentStatusSerializers(data={
                'user': self.user.id,
                'booking_payment': payment_record.id,
                'payment_confirmed': True,
                'payment_completed': False,
                'booking': self.booking_id,
                'payment_canceled': False,
                'confirmed_at': timezone.now(),
                'to_be_refunded': False
            })
            
            if not payment_status_serializer.is_valid():
                self.logger.error(f"Payment status serializer errors: {payment_status_serializer.errors}")
                raise Exception("Failed to save payment status")
                
            payment_status_serializer.save()
            
            # Save booking status
            booking_status_serializer = MyBookingStatusSerializers(data={
                'user': self.user.id,
                'booking': self.booking_id,
                'confirmed': True,
                'completed': False,
                'canceled': False,
                'confirmed_at': timezone.now()
            })
            
            if not booking_status_serializer.is_valid():
                self.logger.error(f"Booking status serializer errors: {booking_status_serializer.errors}")
                raise Exception("Failed to save booking status")
                
            booking_status_serializer.save()
            
            return payment_record
            
        except Exception as e:
            self.logger.error(f"Error saving booking payment: {str(e)}")
            raise
    
    @transaction.atomic
    def _save_renting_payment(self, payment_data: Dict[str, Any], transaction_id: str):
        """Save renting payment record with atomic transaction"""
        from .renting_serializers import CreateMyRentingPaymentSerializers, CreateMyRentingPaymentStatusSerializer, CreateMyRentingStatusSerializer
        
        try:
            # Save payment
            payment_serializer = CreateMyRentingPaymentSerializers(data={
                'renting': self.renting_id,
                'user': self.user.id,
                'payment_method': payment_data['payment_method'],
                'total_price': float(payment_data['amount']),
                'transaction_id': transaction_id
            })
            
            if not payment_serializer.is_valid():
                self.logger.error(f"Payment serializer errors: {payment_serializer.errors}")
                return None
                
            payment_record = payment_serializer.save()
            
            # Save payment status
            payment_status_serializer = CreateMyRentingPaymentStatusSerializer(data={
                'user': self.user.id,
                'renting': self.renting_id,
                'renting_payment': payment_record.id,
                'payment_confirmed': False,
                'payment_completed': False,
                'payment_canceled': False,
                'confirmed_at': timezone.now()
            })
            
            if not payment_status_serializer.is_valid():
                self.logger.error(f"Payment status serializer errors: {payment_status_serializer.errors}")
                raise Exception("Failed to save payment status")
                
            payment_status_serializer.save()
            
            # Save renting status
            renting_status_serializer = CreateMyRentingStatusSerializer(data={
                'user': self.user.id,
                'renting': self.renting_id,
                'renting_request_confirmed': True,
                'renting_status': 'ongoing',
                'confirmed_at': timezone.now(),
                'started_at': timezone.now()
            })
            
            if not renting_status_serializer.is_valid():
                self.logger.error(f"Renting status serializer errors: {renting_status_serializer.errors}")
                raise Exception("Failed to save renting status")
                
            renting_status_serializer.save()
            
            return payment_record
            
        except Exception as e:
            self.logger.error(f"Error saving renting payment: {str(e)}")
            raise


class PaymentStatusManager:
    """Utility for managing payment status"""
    
    @staticmethod
    def get_payment_status(transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Get payment status by transaction ID
        
        Args:
            transaction_id: Transaction ID to check
            
        Returns:
            Payment status information or None
        """
        try:
            # Check booking payments
            try:
                booking_payment = MyBookingPayment.objects.get(transaction_id=transaction_id)
                payment_status = MyBookingPaymentStatus.objects.get(booking_payment=booking_payment)
                
                return {
                    'type': 'booking',
                    'payment_id': booking_payment.id,
                    'booking_id': booking_payment.booking.id,
                    'user_id': booking_payment.user.id,
                    'payment_method': booking_payment.payment_method,
                    'transaction_id': transaction_id,
                    'confirmed': payment_status.payment_confirmed,
                    'completed': payment_status.payment_completed,
                    'canceled': payment_status.payment_canceled,
                    'confirmed_at': payment_status.confirmed_at,
                    'completed_at': payment_status.completed_at,
                    'canceled_at': payment_status.canceled_at
                }
            except (MyBookingPayment.DoesNotExist, MyBookingPaymentStatus.DoesNotExist):
                pass
            
            # Check renting payments
            try:
                renting_payment = MyRentingPayment.objects.get(transaction_id=transaction_id)
                payment_status = MyRentingPaymentStatus.objects.get(renting_payment=renting_payment)
                
                return {
                    'type': 'renting',
                    'payment_id': renting_payment.id,
                    'renting_id': renting_payment.renting.id,
                    'user_id': renting_payment.user.id,
                    'payment_method': renting_payment.payment_method,
                    'transaction_id': transaction_id,
                    'confirmed': payment_status.payment_confirmed,
                    'completed': payment_status.payment_completed,
                    'canceled': payment_status.payment_canceled,
                    'confirmed_at': payment_status.confirmed_at,
                    'completed_at': payment_status.completed_at,
                    'canceled_at': payment_status.canceled_at
                }
            except (MyRentingPayment.DoesNotExist, MyRentingPaymentStatus.DoesNotExist):
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            return None
    
    @staticmethod
    def update_payment_status(transaction_id: str, status: str, message: str = None) -> bool:
        """
        Update payment status
        
        Args:
            transaction_id: Transaction ID
            status: New status
            message: Optional status message
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            payment_info = PaymentStatusManager.get_payment_status(transaction_id)
            if not payment_info:
                return False
            
            if payment_info['type'] == 'booking':
                payment_status = MyBookingPaymentStatus.objects.get(
                    booking_payment_id=payment_info['payment_id']
                )
                
                if status.upper() == PaymentStatus.SUCCESS:
                    payment_status.payment_confirmed = True
                    payment_status.payment_completed = True
                    payment_status.payment_canceled = False
                    payment_status.completed_at = timezone.now()
                elif status.upper() in [PaymentStatus.FAILED, PaymentStatus.CANCELLED]:
                    payment_status.payment_confirmed = False
                    payment_status.payment_completed = False
                    payment_status.payment_canceled = True
                    payment_status.canceled_at = timezone.now()
                
                payment_status.save()
                
            elif payment_info['type'] == 'renting':
                payment_status = MyRentingPaymentStatus.objects.get(
                    renting_payment_id=payment_info['payment_id']
                )
                
                if status.upper() == PaymentStatus.SUCCESS:
                    payment_status.payment_confirmed = True
                    payment_status.payment_completed = True
                    payment_status.payment_canceled = False
                    payment_status.completed_at = timezone.now()
                elif status.upper() in [PaymentStatus.FAILED, PaymentStatus.CANCELLED]:
                    payment_status.payment_confirmed = False
                    payment_status.payment_completed = False
                    payment_status.payment_canceled = True
                    payment_status.canceled_at = timezone.now()
                
                payment_status.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating payment status: {str(e)}")
            return False
