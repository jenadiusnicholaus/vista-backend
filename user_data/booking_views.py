from property.paginators import CustomPageNumberPagination
from .models import MyBookingStatus, MyBooking, MyPaymentCard
from user_data.azam_pay_checkout import AzamPayCheckout
from user_data.azam_res_models import TransactionResponse
from user_data.global_serializers import PropertyStatusUpdateSerializer
from user_data.booking_serializers import  CreateMyBookingSerializers, GetMyBookingSerializers, GetMyBookingStatusSerializers, MyBookingPaymentSerializers, MyBookingPaymentStatusSerializers, MyBookingStatusSerializers, MyPaymentCardSerializers
from rest_framework import viewsets, status 
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
import logging as logger
import json


class MybookingInforsViewSet(viewsets.ModelViewSet):
    queryset = MyBooking.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GetMyBookingSerializers

    def list(self, request, *args, **kwargs):
       
        try:
            # Assuming `request.user` is the way to get the current user. Adjust as necessary.
            property_id = request.query_params.get('property_id', None)
            user_specific_queryset = self.queryset.filter(user=request.user, property_id = property_id).latest('created_at')
            serializer = self.get_serializer(user_specific_queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except self.queryset.model.DoesNotExist:  
            return Response({'message': 'Not Booking, please Add one now.'}, status=status.HTTP_400_BAD_REQUEST)
        
    def create(self, request, *args, **kwargs): 
        print(request.data)
        user = request.user
        check_in = request.data.get('check_in', None)
        check_out = request.data.get('check_out', None)
        total_guest = request.data.get('total_guest', None)
        total_price = request.data.get('total_price', None)
        adult = request.data.get('adult', None)
        children = request.data.get('children', None)
        serializers = CreateMyBookingSerializers(data={
            'user': user.id,
            "property": request.query_params.get('property_id', None),  
            'check_in': check_in,
            'check_out': check_out,
            'total_guest': int(adult) + int(children),
            'total_price': total_price,
            'adult': adult,
            'children': children
        })
        if serializers.is_valid():
            serializers.save()
            return Response(
                {
                    'message': 'Booking information added successfully.',
                }, status=status.HTTP_201_CREATED)
        else: 
            
            return Response(
                {
                    'message': 'Booking information not added.',
                    'data': serializers.errors
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
            print(e)
            return Response({'message': 'An error occurred.', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        


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
        booking_id = request.query_params.get('booking_id', None)
        user = request.user
        payment_method = request.data.get('payment_method', None)
        accountNumber = request.data.get('accountNumber', None)
        amount = request.data.get('amount', None)

        if not all([booking_id, payment_method, accountNumber, amount]):
            return Response(
                {
                    "message": "Missing required parameters."
                }, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get payment gateway authentication
            azmpay = AzamPayCheckout(
                accountNumber=accountNumber,
                amount=amount,
                externalId=booking_id,
                provider=payment_method,
            )
        except Exception as e:
            return Response(
                {
                    "message": "Failed to authenticate with payment gateway",
                    "data": str(e),
                }, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get payment response from payment gateway
            response = azmpay.initCheckout()
            responseModel = TransactionResponse(**json.loads(response))
        except Exception as e:
            return Response(
                {
                    "message": "Error creating checkout",
                    "data": str(e),
                }, status=status.HTTP_400_BAD_REQUEST
            )

        if not responseModel.success:
            return Response(
                {
                    "message": "Payment failed",
                    "data": responseModel.message
                }, status=status.HTTP_400_BAD_REQUEST
            )
        else:

        
            pszls = MyBookingPaymentSerializers(data={
                'booking': booking_id,
                'user': user.id,
                'payment_method': payment_method,
                'transaction_id': responseModel.transactionId
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
                        logger.error(bookingStatusSzs.errors)  
                        return Response(
                            {
                                'message': 'Booking not confirmed.',
                                'data': bookingStatusSzs.errors
                            }, status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    logger.error(pStatusSzs.errors)
                    return Response(
                        {
                            'message': 'Booking not confirmed.',
                            'data': pStatusSzs.errors
                        }, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                logger.error(pszls.errors)
                return Response(
                    {
                        'message': 'Booking not confirmed.',
                        'data': pszls.errors
                    }, status=status.HTTP_400_BAD_REQUEST
                )
            

    def update_property_status(request, booking_id):
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
        queryset = self.queryset.filter(user=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    