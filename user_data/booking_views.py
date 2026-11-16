from property.paginators import CustomPageNumberPagination
from .models import MyBookingStatus, MyBooking, MyPaymentCard
from property.models import Property
from user_data.azam_pay_checkout import AzamPayCheckout
from user_data.azam_res_models import TransactionResponse
from user_data.global_serializers import PropertyStatusUpdateSerializer
from user_data.booking_serializers import  CreateMyBookingSerializers, GetMyBookingSerializers, GetMyBookingStatusSerializers, MyBookingPaymentSerializers, MyBookingPaymentStatusSerializers, MyBookingStatusSerializers, MyPaymentCardSerializers
from rest_framework import viewsets, status 
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
import logging
import json
import re


class MybookingInforsViewSet(viewsets.ModelViewSet):
    queryset = MyBooking.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GetMyBookingSerializers

    def list(self, request, *args, **kwargs):
        property_id = request.query_params.get('property_id', None)
        
        if not property_id:
            return Response({
                'message': 'Property ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Check if property exists
            property_obj = Property.objects.get(id=property_id)
            
            # If property is available, return booking info only if it's pending/unconfirmed
            if property_obj.availability_status:
                try:
                    from .models import MyBookingStatus
                    
                    # Get user's latest booking for this property
                    user_booking = self.queryset.filter(
                        user=request.user, 
                        property_id=property_id
                    ).latest('created_at')
                    
                    # Check if booking has pending/unconfirmed status
                    try:
                        booking_status = MyBookingStatus.objects.filter(booking=user_booking).latest('created_at')
                        
                        # Only return booking if it's NOT confirmed (pending status)
                        if not booking_status.confirmed:
                            serializer = self.get_serializer(user_booking)
                            booking_data = serializer.data
                            booking_data['message'] = 'Property is available. Showing pending booking.'
                            booking_data['property_available'] = True
                            booking_data['my_booking_status'] = {
                                'id': booking_status.id,
                                'confirmed': booking_status.confirmed,
                                'completed': booking_status.completed,
                                'canceled': booking_status.canceled,
                                'confirmed_at': booking_status.confirmed_at,
                                'completed_at': booking_status.completed_at,
                                'canceled_at': booking_status.canceled_at,
                                'created_at': booking_status.created_at,
                                'updated_at': booking_status.updated_at
                            }
                            
                            return Response(booking_data, status=status.HTTP_200_OK)
                            
                    except MyBookingStatus.DoesNotExist:
                        # No booking status means it's pending
                        serializer = self.get_serializer(user_booking)
                        booking_data = serializer.data
                        booking_data['message'] = 'Property is available. Showing pending booking.'
                        booking_data['property_available'] = True
                        booking_data['my_booking_status'] = None  # No status record exists
                        
                        return Response(booking_data, status=status.HTTP_200_OK)
                    
                except self.queryset.model.DoesNotExist:
                    pass
                    
                # No pending booking found or user has no booking at all
                return Response({
                    'message': 'Property is available. User has no booking or no pending booking.',
                    'property_available': True,
                    'has_booking': False
                }, status=status.HTTP_200_OK)
            
            # Property is not available, check if user has an active booking for this property
            try:
                from .models import MyBookingStatus
                
                # Get user's booking for this property
                user_booking = self.queryset.filter(
                    user=request.user, 
                    property_id=property_id
                ).latest('created_at')
                
                # Check if this booking has an active status (confirmed and not completed/canceled)
                try:
                    booking_status = MyBookingStatus.objects.filter(booking=user_booking).latest('created_at')
                    
                    # Check if booking is active (confirmed but not completed or canceled)
                    if booking_status.confirmed and not booking_status.completed and not booking_status.canceled:
                        # Check if booking dates are still active (check-out date hasn't passed)
                        from django.utils import timezone
                        from datetime import datetime
                        
                        current_date = timezone.now().date()
                        
                        if user_booking.check_out >= current_date:
                            # Booking is active
                            serializer = self.get_serializer(user_booking)
                            booking_data = serializer.data
                            booking_data['booking_status'] = 'active'
                            booking_data['property_available'] = False
                            
                            return Response(booking_data, status=status.HTTP_200_OK)
                
                except MyBookingStatus.DoesNotExist:
                    pass
                
                # If we reach here, user has booking but it's not active
                return Response({
                    'message': 'Property is not available and you have no active booking.',
                    'property_available': False
                }, status=status.HTTP_200_OK)
                
            except self.queryset.model.DoesNotExist:
                # User has no booking for this property
                return Response({
                    'message': 'Property is not available and you have no booking for this property.',
                    'property_available': False
                }, status=status.HTTP_200_OK)
                
        except Property.DoesNotExist:
            return Response({
                'message': 'Property not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
    def create(self, request, *args, **kwargs):
        logger = logging.getLogger(__name__)
        user = request.user
        
        property_id = request.query_params.get('property_id', None)
        if not property_id:
            return Response({
                'message': 'Property ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if property exists and is available
        try:
            property_obj = Property.objects.get(id=property_id)
            if not property_obj.availability_status:
                return Response({
                    'message': 'Property is not available for booking'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Property.DoesNotExist:
            return Response({
                'message': 'Property not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Regular booking creation - validate all required fields
        required_fields = ['check_in', 'check_out', 'total_price', 'adult', 'children']
        missing_fields = [field for field in required_fields if not request.data.get(field)]
        
        if missing_fields:
            return Response({
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        check_in = request.data.get('check_in')
        check_out = request.data.get('check_out')
        total_price = request.data.get('total_price')
        adult = request.data.get('adult')
        children = request.data.get('children')
        
        # Validate numeric fields
        try:
            adult = int(adult)
            children = int(children)
            total_price = Decimal(str(total_price))
            
            if adult < 0 or children < 0:
                raise ValueError("Guest counts cannot be negative")
            if total_price <= 0:
                raise ValueError("Total price must be positive")
                
        except (ValueError, InvalidOperation) as e:
            return Response({
                'message': f'Invalid numeric values: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        booking_data = {
            'user': user.id,
            "property": property_id,  
            'check_in': check_in,
            'check_out': check_out,
            'total_guest': int(adult) + int(children),
            'total_price': total_price,
            'adult': adult,
            'children': children
        }
        
        serializers = CreateMyBookingSerializers(data=booking_data)
        if serializers.is_valid():
            booking_instance = serializers.save()
            logger.info(f"Booking created successfully with ID: {booking_instance.id}")
            return Response(
                {
                    'message': 'Booking information added successfully.',
                    'booking_id': booking_instance.id,
                    'data': serializers.data
                }, status=status.HTTP_201_CREATED)
        else: 
            logger.error(f"Booking creation failed: {serializers.errors}")
            return Response(
                {
                    'message': 'Booking information not added.',
                    'errors': serializers.errors
                },
                 status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request):
        try:
            # Assuming you get booking_id from somewhere, e.g., from the request
            booking_id = request.query_params.get('booking_info_id', None)
            booking_info = MyBooking.objects.get(id=booking_id)
            check_in = request.data.get('check_in', None)
            check_out = request.data.get('check_out', None)
            total_guest = request.data.get('total_guest', None)
            total_price = request.data.get('total_price', None)
            adult = request.data.get('adult', None)
            children = request.data.get('children', None)
            
            if request.user == booking_info.user:  # Assuming the booking has a user field for authorization
                serializer = self.get_serializer(booking_info, data={
                    'check_in': check_in,
                    'check_out': check_out,
                    'total_guest': int(adult) + int(children),
                    'total_price': total_price,
                    'adult': adult,
                    'children': children
                
                }, partial=True)


                if serializer.is_valid():
                    serializer.save()
                    # cancelation_serializer.save()
                    return Response({'message': 'Booking information updated successfully.'}, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'You are not authorized to update this booking information.'}, status=status.HTTP_403_FORBIDDEN)
        except MyBooking.DoesNotExist:
            return Response({'message': 'Booking information not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'Error updating booking: {str(e)}')
            return Response({'message': 'An error occurred while updating booking.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        


class MyBankPaymentDetailsViewSet(viewsets.ModelViewSet):
    queryset = MyPaymentCard.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = MyPaymentCardSerializers

    def create(self, request, *args, **kwargs):
        user = request.user
        card_number = request.data.get('account_number', None)
        card_holder_name = request.data.get('card_holder_name', None)
        card_expiry = request.data.get('card_expiry', None)
        card_cvv = request.data.get('card_cvv', None)
        bank_name = request.data.get('bank_name', None)


        serializers = self.get_serializer(data={
            'user': user.id,
            'account_number': card_number,
            'card_holder_name': card_holder_name,
            'card_expiry': card_expiry,
            'card_cvv': card_cvv,
            'bank_name': bank_name
        })
        if serializers.is_valid():
            serializers.save()
            return Response(
                {
                    'message': 'Payment card details added successfully.',
                }, status=status.HTTP_201_CREATED)

        else:
            return Response(
                {
                    'message': 'Payment card details not added.',
                    'data': serializers.errors
                },
                 status=status.HTTP_400_BAD_REQUEST)  


    
    def patch(self, request):
        try:
            # Assuming you get card_id from somewhere, e.g., from the request
            card_id = request.query_params.get('card_info_id', None)
            card_info = MyPaymentCard.objects.get(id=card_id)
            card_number = request.data.get('account_number', None)
            card_holder_name = request.data.get('card_holder_name', None)
            card_expiry = request.data.get('card_expiry', None)
            card_cvv = request.data.get('card_cvv', None)
            bank_name = request.data.get('bank_name', None)
            
            if request.user == card_info.user:  # Assuming the card has a user field for authorization
                serializer = self.get_serializer(card_info, data={
                    "bank_name" : bank_name,
                    'account_number': card_number,
                    'card_holder_name': card_holder_name,
                    'card_expiry': card_expiry,
                    'card_cvv': card_cvv
                }, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'message': 'Payment card details updated successfully.'}, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'You are not authorized to update this payment card details.'}, status=status.HTTP_403_FORBIDDEN)
        except MyPaymentCard.DoesNotExist:
            return Response({'message': 'Payment card details not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': 'An error occurred.', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   



class ConfirmBookingViewSet(viewsets.ModelViewSet):
    queryset = MyBookingStatus.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GetMyBookingStatusSerializers

    """
    1. Get booking information
        - check_in
        - check_out
        - total_guest
        - total_price
        - adult
        - children  

    2. Get payment information
        for mobile money    
        - accountNumber
        - amount
        - currency(TZS)
        - externalId
        - provider
    

    3. send payment request to payment gateway
        - get payment status
        - get payment message
        - get payment reference_id
        - get payment transaction_id
        - get payment transaction_status


    4. Once payment is successful UPdate or create MyBookingPayment, MyBookingStatus, MyBookingPaymentStatus Table
        - save booking information
        - save payment information
        - save payment status
        - save booking status
        - save payment reference_id
        - save payment transaction_id
        - save payment transaction_status
        - save payment message
    
    5. Return success message
     else return error message  

    """

    def get_object(self):
        booking_id = self.request.query_params.get('booking_id', None)
        return self.queryset.get(booking=booking_id)
   
    # def list(self, request, *args, **kwargs):
    #     try:
    #         instance = self.get_object()
    #         serializer = self.get_serializer(instance)
    #         return Response(serializer.data)
    #     except MyBookingStatus.DoesNotExist:
    #         return Response({'message': 'Booking status not found.'}, status=status.HTTP_404_NOT_FOUND)       
    def create(self, request, *args, **kwargs):
        logger = logging.getLogger(__name__)
        booking_id = request.query_params.get('booking_id', None)
        user = request.user
        payment_method = request.data.get('payment_method', None)
        accountNumber = request.data.get('accountNumber', None)
        amount = request.data.get('amount', None)

        # Validate required parameters
        if not all([booking_id, payment_method, accountNumber, amount]):
            return Response({
                "message": "Missing required parameters: booking_id, payment_method, accountNumber, amount"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate booking exists and belongs to user
        try:
            booking = MyBooking.objects.get(id=booking_id, user=user)
        except MyBooking.DoesNotExist:
            return Response({
                "message": "Booking not found or access denied"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError):
            return Response({
                "message": "Invalid amount format"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate phone number format
        phone_pattern = r'^(071|065|067|078|068|075|062|076|074)\d{7}$'
        if not re.match(phone_pattern, str(accountNumber)):
            return Response({
                "message": "Invalid phone number format. Must be a valid Tanzanian mobile number"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate payment method
        from .azam_res_models import PaymentProvider
        if not PaymentProvider.is_valid_provider(payment_method):
            valid_providers = PaymentProvider.get_all_providers()
            return Response({
                "message": f"Invalid payment method. Must be one of: {', '.join(valid_providers)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize provider name
        payment_method = PaymentProvider.normalize_provider(payment_method)

        # Initialize payment gateway
        try:
            azmpay = AzamPayCheckout(
                accountNumber=accountNumber,
                amount=amount,
                externalId=booking_id,
                provider=payment_method,
            )
            
            # Validate phone number for specific provider
            if not azmpay.validate_phone_number(accountNumber, payment_method):
                return Response({
                    "message": f"Phone number {accountNumber} is not valid for {payment_method} network"
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Payment gateway initialization failed: {str(e)}")
            return Response({
                "message": "Failed to initialize payment gateway",
                "error": "Please check your payment details and try again"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Process payment
        try:
            response = azmpay.initCheckout()
            
            # Validate response structure
            if not isinstance(response, dict):
                raise ValueError("Invalid response format from payment gateway")
            
            if not response.get('success', False):
                error_message = response.get('message', 'Payment failed')
                return Response({
                    "message": "Payment failed",
                    "error": error_message
                }, status=status.HTTP_400_BAD_REQUEST)
            
            transaction_id = response.get('transactionId')
            if not transaction_id:
                raise ValueError("No transaction ID received")
                
            logger.info(f"Payment initiated successfully for booking {booking_id}, transaction: {transaction_id}")
            
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            return Response({
                "message": "Payment processing failed",
                "error": "Please try again or contact support"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Save payment information
        try:

            pszls = MyBookingPaymentSerializers(data={
                'booking': booking_id,
                'user': user.id,
                'payment_method': payment_method,
                'transaction_id': transaction_id
            })
            if pszls.is_valid():
                pszls.save()
                pStatusSzs = MyBookingPaymentStatusSerializers(data={
                    'user': user.id,
                    'booking_payment': pszls.data['id'],
                    'payment_confirmed': True,
                    'payment_completed': False,
                    "booking": booking_id,
                    'payment_canceled': False,
                    'confirmed_at': timezone.now(),
                    'to_be_refunded': False
                })
                if pStatusSzs.is_valid():
                    pStatusSzs.save()
                    bookingStatusSzs = MyBookingStatusSerializers(data={
                        'user': user.id,
                        'booking': booking_id,
                        'confirmed': True,
                        'completed': False,
                        'canceled': False,
                        'confirmed_at': timezone.now()
                    })
                    if bookingStatusSzs.is_valid():
                        bookingStatusSzs.save()

                        # final update booked property status
                        self.update_property_status(booking_id)

                        return Response(
                            {
                                'message': 'Booking confirmed successfully.',
                            }, status=status.HTTP_201_CREATED
                        )
                        # // update property status to not available
                    else:
                        logger.error(f"Booking status creation failed: {bookingStatusSzs.errors}")
                        return Response({
                            'message': 'Failed to create booking status record'
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    logger.error(f"Payment status creation failed: {pStatusSzs.errors}")
                    return Response({
                        'message': 'Failed to create payment status record'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                logger.error(f"Payment record creation failed: {pszls.errors}")
                return Response({
                    'message': 'Failed to create payment record'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error saving payment data: {str(e)}")
            return Response({
                'message': 'Failed to save payment information'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

    def update_property_status(self, booking_id):
        try:
            booking = MyBooking.objects.get(id=booking_id)
            property_instance = booking.property
            
            # Create a serializer instance with the data to be updated
            serializer = PropertyStatusUpdateSerializer(
                property_instance, 
                data={'availability_status': False}, 
                partial=True
            )
            
            # Validate and save the data
            if serializer.is_valid():
                serializer.save()
                
            else:
                return Response(
                    {"message": "Invalid data.", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except MyBooking.DoesNotExist:
            return Response(
                {"message": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND
            )
class BookingRequestViewSet(viewsets.ModelViewSet):
    queryset  = MyBooking.objects.filter()
    serializer_class = GetMyBookingSerializers
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination


    def list(self, request, *args, **kwargs):
        # paginaye it
        user = request.user
        queryset = self.queryset.filter(user=user).order_by('-created_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get the latest booking for the authenticated user"""
        try:
            user = request.user
            latest_booking = MyBooking.objects.filter(user=user).latest('created_at')
            serializer = self.get_serializer(latest_booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MyBooking.DoesNotExist:
            return Response({
                'message': 'No bookings found for this user.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def for_duplication(self, request):
        """Get user's previous bookings that can be duplicated"""
        user = request.user
        limit = request.query_params.get('limit', 10)
        
        try:
            limit = int(limit)
            if limit > 50:  # Prevent excessive data retrieval
                limit = 50
        except (ValueError, TypeError):
            limit = 10
            
        # Get user's previous bookings, ordered by most recent
        bookings = MyBooking.objects.filter(user=user).order_by('-created_at')[:limit]
        
        if not bookings.exists():
            return Response({
                'message': 'No previous bookings found for duplication.',
                'data': []
            }, status=status.HTTP_200_OK)
        
        # Create simplified data for duplication selection
        booking_data = []
        for booking in bookings:
            booking_data.append({
                'id': booking.id,
                'property_name': booking.property.name,
                'property_id': booking.property.id,
                'check_in': booking.check_in,
                'check_out': booking.check_out,
                'total_guest': booking.total_guest,
                'total_price': booking.total_price,
                'adult': booking.adult,
                'children': booking.children,
                'created_at': booking.created_at,
                'property_image': booking.property.property_images.first().image.url if booking.property.property_images.exists() else None
            })
        
        return Response({
            'message': 'Previous bookings retrieved successfully.',
            'count': len(booking_data),
            'data': booking_data
        }, status=status.HTTP_200_OK)
    
    