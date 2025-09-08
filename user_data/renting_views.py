


from property.paginators import CustomPageNumberPagination
from user_data.azam_pay_checkout import AzamPayCheckout
from user_data.azam_res_models import TransactionResponse
from user_data.payment_utils import PaymentValidator, PaymentProcessor
from user_data.global_serializers import PropertyStatusUpdateSerializer
from user_data.models import MyRenting, MyRentingStatus
from user_data.renting_serializers import CreateMyRentingSerializer, CreateMyRentingPaymentSerializers, CreateMyRentingPaymentStatusSerializer, CreateMyRentingStatusSerializer, MyRentingSerializer, MyRentingStatusSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
import logging
import json
import re



class MyRentingModelViewSet(viewsets.ModelViewSet):
    queryset = MyRenting.objects.filter()
    serializer_class = MyRentingSerializer
    permission_classes = [IsAuthenticated]
    def list(self, request, *args, **kwargs):
      
        try:
            queryset = self.filter_queryset(self.get_queryset()).filter(user=request.user, property__id =request.query_params.get('property_id')).latest('created_at')
            serializer = self.get_serializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MyRenting.DoesNotExist:
            return Response({"message": "No renting found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f'Error retrieving renting: {str(e)}')
            return Response({"message": "An error occurred while retrieving renting."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def create(self, request, *args, **kwargs):
        logger = logging.getLogger(__name__)
        
        # Validate required fields
        required_fields = ['property', 'renting_duration', 'total_price', 'check_in', 'check_out', 'total_family_member', 'adult', 'children']
        missing_fields = [field for field in required_fields if not request.data.get(field)]
        
        if missing_fields:
            return Response({
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate numeric fields
        try:
            adult = int(request.data.get('adult'))
            children = int(request.data.get('children'))
            total_family_member = int(request.data.get('total_family_member'))
            total_price = Decimal(str(request.data.get('total_price')))
            
            if adult < 0 or children < 0 or total_family_member < 0:
                raise ValueError("Family member counts cannot be negative")
            if total_price <= 0:
                raise ValueError("Total price must be positive")
            if adult + children != total_family_member:
                raise ValueError("Total family members should equal adult + children")
                
        except (ValueError, InvalidOperation) as e:
            return Response({
                'message': f'Invalid numeric values: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = {
            'property': request.data.get('property'),
            'renting_duration': request.data.get('renting_duration'),
            'total_price': total_price,
            'check_in': request.data.get('check_in'),
            'check_out': request.data.get('check_out'),
            'total_family_member': total_family_member,
            'adult': adult,
            'children': children,
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
        logger = logging.getLogger(__name__)
        renting_id = request.query_params.get('renting_id', None)
        user = request.user
        payment_method = request.data.get('payment_method', None)
        accountNumber = request.data.get('accountNumber', None)
        amount = request.data.get('amount', None)

        # Validate required parameters
        if not all([renting_id, payment_method, accountNumber, amount]):
            return Response({
                "message": "Missing required parameters: renting_id, payment_method, accountNumber, amount"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate renting exists and belongs to user
        try:
            renting = MyRenting.objects.get(id=renting_id, user=user)
        except MyRenting.DoesNotExist:
            return Response({
                "message": "Renting not found or access denied"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Validate payment data using utility
        payment_data = {
            'payment_method': payment_method,
            'account_number': accountNumber,
            'amount': amount
        }
        
        is_valid, error_message = PaymentValidator.validate_payment_request(payment_data)
        if not is_valid:
            return Response({
                "message": error_message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize provider name
        from .azam_res_models import PaymentProvider
        payment_method = PaymentProvider.normalize_provider(payment_method)

        # Process payment using PaymentProcessor utility
        try:
            processor = PaymentProcessor(user=user, renting_id=renting_id)
            
            result = processor.process_payment(payment_data)
            
            if not result['success']:
                return Response({
                    "message": result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update property status after successful payment
            self.update_property_status(renting_id)
            
            return Response({
                'message': 'Renting confirmed successfully.',
                'transaction_id': result.get('transaction_id'),
                'payment_id': result.get('payment_id')
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            return Response({
                "message": "Payment processing failed",
                "error": "Please try again or contact support"
            }, status=status.HTTP_400_BAD_REQUEST)
            

    def update_property_status(self, renting_id):
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
        
class MyRentingRequestViewSet(viewsets.ModelViewSet):
    queryset = MyRenting.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = MyRentingSerializer
    pagination_class = CustomPageNumberPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    


        
    


        
       

       
    