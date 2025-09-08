import json
import logging
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .models import MyBooking, MyBookingPayment, MyBookingPaymentStatus, MyBookingStatus
from .azam_pay_checkout import AzamPayCheckout
from .booking_serializers import MyBookingPaymentStatusSerializers, MyBookingStatusSerializers

logger = logging.getLogger(__name__)


class AzamPayWebhookView(APIView):
    """
    Webhook endpoint for Azam Pay payment notifications
    """
    permission_classes = [AllowAny]
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Handle incoming webhook notifications from Azam Pay"""
        try:
            # Log the incoming webhook
            logger.info(f"Received webhook: {request.body.decode('utf-8')}")
            
            # Parse webhook data
            webhook_data = request.data
            
            # Validate webhook structure
            required_fields = ['transactionId', 'externalId', 'status', 'message']
            missing_fields = [field for field in required_fields if field not in webhook_data]
            
            if missing_fields:
                logger.error(f"Missing webhook fields: {missing_fields}")
                return Response({
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            transaction_id = webhook_data.get('transactionId')
            external_id = webhook_data.get('externalId')  # This should be our booking_id
            payment_status = webhook_data.get('status')
            message = webhook_data.get('message')
            amount = webhook_data.get('amount')
            
            logger.info(f"Processing webhook for transaction {transaction_id}, booking {external_id}, status: {payment_status}")
            
            # Find the payment record
            try:
                payment = MyBookingPayment.objects.get(
                    transaction_id=transaction_id,
                    booking_id=external_id
                )
            except MyBookingPayment.DoesNotExist:
                logger.error(f"Payment record not found for transaction {transaction_id}")
                return Response({
                    'error': 'Payment record not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Process different payment statuses
            if payment_status.upper() == 'SUCCESS':
                self._handle_successful_payment(payment, webhook_data)
            elif payment_status.upper() == 'FAILED':
                self._handle_failed_payment(payment, webhook_data)
            elif payment_status.upper() == 'CANCELLED':
                self._handle_cancelled_payment(payment, webhook_data)
            elif payment_status.upper() == 'PENDING':
                self._handle_pending_payment(payment, webhook_data)
            else:
                logger.warning(f"Unknown payment status: {payment_status}")
            
            return Response({
                'message': 'Webhook processed successfully'
            }, status=status.HTTP_200_OK)
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook")
            return Response({
                'error': 'Invalid JSON format'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return Response({
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _handle_successful_payment(self, payment, webhook_data):
        """Handle successful payment notification"""
        try:
            # Update payment status
            payment_status, created = MyBookingPaymentStatus.objects.get_or_create(
                booking_payment=payment,
                defaults={
                    'user': payment.user,
                    'booking': payment.booking,
                    'payment_confirmed': True,
                    'payment_completed': True,
                    'payment_canceled': False,
                    'confirmed_at': timezone.now(),
                    'completed_at': timezone.now(),
                    'to_be_refunded': False
                }
            )
            
            if not created:
                # Update existing record
                payment_status.payment_confirmed = True
                payment_status.payment_completed = True
                payment_status.payment_canceled = False
                payment_status.completed_at = timezone.now()
                payment_status.save()
            
            # Update booking status
            booking_status, created = MyBookingStatus.objects.get_or_create(
                booking=payment.booking,
                defaults={
                    'user': payment.user,
                    'confirmed': True,
                    'completed': False,
                    'canceled': False,
                    'confirmed_at': timezone.now()
                }
            )
            
            if not created:
                booking_status.confirmed = True
                booking_status.canceled = False
                booking_status.confirmed_at = timezone.now()
                booking_status.save()
            
            # Update property availability
            self._update_property_availability(payment.booking, False)
            
            logger.info(f"Payment {payment.transaction_id} marked as successful")
            
        except Exception as e:
            logger.error(f"Error handling successful payment: {str(e)}")
            raise
    
    def _handle_failed_payment(self, payment, webhook_data):
        """Handle failed payment notification"""
        try:
            # Update payment status
            payment_status, created = MyBookingPaymentStatus.objects.get_or_create(
                booking_payment=payment,
                defaults={
                    'user': payment.user,
                    'booking': payment.booking,
                    'payment_confirmed': False,
                    'payment_completed': False,
                    'payment_canceled': True,
                    'canceled_at': timezone.now(),
                    'to_be_refunded': False
                }
            )
            
            if not created:
                payment_status.payment_confirmed = False
                payment_status.payment_completed = False
                payment_status.payment_canceled = True
                payment_status.canceled_at = timezone.now()
                payment_status.save()
            
            # Update booking status
            booking_status, created = MyBookingStatus.objects.get_or_create(
                booking=payment.booking,
                defaults={
                    'user': payment.user,
                    'confirmed': False,
                    'completed': False,
                    'canceled': True,
                    'canceled_at': timezone.now()
                }
            )
            
            if not created:
                booking_status.confirmed = False
                booking_status.canceled = True
                booking_status.canceled_at = timezone.now()
                booking_status.save()
            
            logger.info(f"Payment {payment.transaction_id} marked as failed")
            
        except Exception as e:
            logger.error(f"Error handling failed payment: {str(e)}")
            raise
    
    def _handle_cancelled_payment(self, payment, webhook_data):
        """Handle cancelled payment notification"""
        try:
            # Similar to failed payment handling
            self._handle_failed_payment(payment, webhook_data)
            logger.info(f"Payment {payment.transaction_id} marked as cancelled")
            
        except Exception as e:
            logger.error(f"Error handling cancelled payment: {str(e)}")
            raise
    
    def _handle_pending_payment(self, payment, webhook_data):
        """Handle pending payment notification"""
        try:
            # Update payment status to pending
            payment_status, created = MyBookingPaymentStatus.objects.get_or_create(
                booking_payment=payment,
                defaults={
                    'user': payment.user,
                    'booking': payment.booking,
                    'payment_confirmed': False,
                    'payment_completed': False,
                    'payment_canceled': False,
                    'to_be_refunded': False
                }
            )
            
            if not created:
                payment_status.payment_confirmed = False
                payment_status.payment_completed = False
                payment_status.payment_canceled = False
                payment_status.save()
            
            logger.info(f"Payment {payment.transaction_id} marked as pending")
            
        except Exception as e:
            logger.error(f"Error handling pending payment: {str(e)}")
            raise
    
    def _update_property_availability(self, booking, available):
        """Update property availability status"""
        try:
            from .global_serializers import PropertyStatusUpdateSerializer
            
            property_instance = booking.property
            serializer = PropertyStatusUpdateSerializer(
                property_instance,
                data={'availability_status': available},
                partial=True
            )
            
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Property {property_instance.id} availability updated to {available}")
            else:
                logger.error(f"Failed to update property availability: {serializer.errors}")
                
        except Exception as e:
            logger.error(f"Error updating property availability: {str(e)}")


class PaymentStatusCheckView(APIView):
    """
    Manual payment status check endpoint
    """
    permission_classes = [AllowAny]  # You might want to add authentication
    
    def post(self, request, *args, **kwargs):
        """Manually check payment status"""
        try:
            transaction_id = request.data.get('transaction_id')
            if not transaction_id:
                return Response({
                    'error': 'Transaction ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Find the payment record
            try:
                payment = MyBookingPayment.objects.get(transaction_id=transaction_id)
            except MyBookingPayment.DoesNotExist:
                return Response({
                    'error': 'Payment record not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Initialize Azam Pay checkout to check status
            azmpay = AzamPayCheckout(
                accountNumber="000000000",  # Dummy values for status check
                amount=1,
                externalId=str(payment.booking.id),
                provider="AIRTEL"
            )
            
            # Get payment status from Azam Pay
            status_response = azmpay.get_payment_status(transaction_id)
            
            return Response({
                'transaction_id': transaction_id,
                'status': status_response,
                'local_payment_status': {
                    'payment_confirmed': payment.mybookingpaymentstatus.payment_confirmed,
                    'payment_completed': payment.mybookingpaymentstatus.payment_completed,
                    'payment_canceled': payment.mybookingpaymentstatus.payment_canceled
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error checking payment status: {str(e)}")
            return Response({
                'error': 'Failed to check payment status'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
