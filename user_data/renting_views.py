


from user_data.azam_pay_checkout import AzamPayCheckout
from user_data.azam_res_models import TransactionResponse
from user_data.global_serializers import PropertyStatusUpdateSerializer
from user_data.models import MyRenting, MyRentingStatus
from user_data.renting_serializers import CreateMyRentingSerializer, CreateMyRentingPaymentSerializers, CreateMyRentingPaymentStatusSerializer, CreateMyRentingStatusSerializer, MyRentingSerializer, MyRentingStatusSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
import logging as logger
import json



class MyRentingModelViewSet(viewsets.ModelViewSet):
    queryset = MyRenting.objects.filter()
    serializer_class = MyRentingSerializer
    permission_classes = [IsAuthenticated]
    def list(self, request, *args, **kwargs):
      
        try:
            queryset = self.filter_queryset(self.get_queryset()).filter(user=request.user, property__id =request.query_params.get('property_id')).latest('created_at')
            serializer = self.get_serializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"message": "No renting found."}, status=status.HTTP_404_NOT_FOUND)
        
    def create(self, request, *args, **kwargs):
      
        data =  {
        
            'property': request.data.get('property'),
            'renting_duration': request.data.get('renting_duration'),
            'total_price': request.data.get('total_price'),
            'check_in': request.data.get('check_in'),
            'check_out': request.data.get('check_out'),
            'total_family_member': request.data.get('total_family_member'),
            'adult': request.data.get('adult'),
            'children': request.data.get('children'),
            'user': request.user.id
        }

        serializer = CreateMyRentingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Renting created successfully",
              }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

    def patch(self, request, *args, **kwargs):
        my_renting = MyRenting.objects.get(id=request.query_params.get('my_renting_id'))
        data = {
            'property': request.data.get('property'),
            'renting_duration': request.data.get('renting_duration'),
            'total_price': request.data.get('total_price'),
            'check_in': request.data.get('check_in'),
            'check_out': request.data.get('check_out'),
            'total_family_member': request.data.get('total_family_member'),
            'adult': request.data.get('adult'),
            'children': request.data.get('children'),
            'user': request.user.id
        }
        serializer = CreateMyRentingSerializer(my_renting, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Renting updated successfully",
              }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ConfirmRentingMWMViewSet(viewsets.ModelViewSet):
    queryset = MyRentingStatus.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = MyRentingStatusSerializer

    """
    1. Get renting information
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


    4. Once payment is successful UPdate or create MyrentingPayment, MyrentingStatus, MyrentingPaymentStatus Table
        - save renting information
        - save payment information
        - save payment status
        - save renting status
        - save payment reference_id
        - save payment transaction_id
        - save payment transaction_status
        - save payment message
    
    5. Return success message
     else return error message  

    """

    def get_object(self):
        renting_id = self.request.query_params.get('renting_id', None)
        return self.queryset.get(renting__id=renting_id)
   
    def list(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except MyRentingStatus.DoesNotExist:
            return Response({'message': 'Renting status not found.'}, status=status.HTTP_404_NOT_FOUND)       
    def create(self, request, *args, **kwargs):
        renting_id = request.query_params.get('renting_id', None)
        user = request.user
        payment_method = request.data.get('payment_method', None)
        accountNumber = request.data.get('accountNumber', None)
        amount = request.data.get('amount', None)

        if not all([renting_id, payment_method, accountNumber, amount]):
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
                externalId=renting_id,
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
 
        
            pszls = CreateMyRentingPaymentSerializers(data={
                'renting': renting_id,
                'user': user.id,
                'payment_method': payment_method,
                "total_price": amount,
                'transaction_id': responseModel.transactionId
            })
            if pszls.is_valid():
                pszls.save()
           
                pStatusSzs = CreateMyRentingPaymentStatusSerializer(data={
                    'user': user.id,
                    'renting': renting_id,
                    'renting_payment': pszls.data['id'],
                    'payment_confirmed': False,
                    'payment_completed': False,
                    'payment_canceled': False,
                    "confirmed_at": timezone.now(),
                   
                })
                if pStatusSzs.is_valid():
                    pStatusSzs.save()
               
                    rentingStatusSzs = CreateMyRentingStatusSerializer(data={
                        'user': user.id,
                        'renting': renting_id,
                        'renting_request_confirmed': True,
                        'renting_status': 'ongoing',
                        'confirmed_at': timezone.now(),
                        'started_at': timezone.now(),
                       
                    })
                    if rentingStatusSzs.is_valid():
                        rentingStatusSzs.save()

                        # final update booked property status
                        self.update_property_status(renting_id)

                        return Response(
                            {
                                'message': 'Renting confirmed successfully.',
                            }, status=status.HTTP_201_CREATED
                        )
                        # // update property status to not available
                    else:
                        logger.error(rentingStatusSzs.errors)  
                        return Response(
                            {
                                'message': 'Renting not confirmed.',
                                'data': rentingStatusSzs.errors
                            }, status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    logger.error(pStatusSzs.errors)
                    return Response(
                        {
                            'message': 'Renting not confirmed.',
                            'data': pStatusSzs.errors
                        }, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                logger.error(pszls.errors)
                return Response(
                    {
                        'message': 'Renting not confirmed.',
                        'data': pszls.errors
                    }, status=status.HTTP_400_BAD_REQUEST
                )
            

    def update_property_status(request, renting_id):
        try:
            renting = MyRenting.objects.get(id=renting_id)
            property_instance = renting.property
            
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
        except MyRenting.DoesNotExist:
            return Response(
                {"message": "renting not found."},
                status=status.HTTP_404_NOT_FOUND
            )

         




        
       

       
    