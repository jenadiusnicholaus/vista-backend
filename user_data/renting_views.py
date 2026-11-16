


from property.paginators import CustomPageNumberPagination
from user_data.azam_pay_checkout import AzamPayCheckout
from user_data.azam_res_models import TransactionResponse
from user_data.payment_utils import PaymentValidator, PaymentProcessor
from user_data.global_serializers import PropertyStatusUpdateSerializer
from user_data.models import MyRenting, MyRentingStatus
from property.models import Property
from user_data.renting_serializers import CreateMyRentingSerializer, CreateMyRentingPaymentSerializers, CreateMyRentingPaymentStatusSerializer, CreateMyRentingStatusSerializer, MyRentingSerializer, MyRentingStatusSerializer
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
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
        property_id = request.query_params.get('property_id', None)
        
        if not property_id:
            return Response({
                'message': 'Property ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Check if property exists
            property_obj = Property.objects.get(id=property_id)
            
            # If property is available, return renting info only if it's pending/unconfirmed
            if property_obj.availability_status:
                try:
                    from .models import MyRentingStatus
                    
                    # Get user's latest renting for this property
                    user_renting = self.queryset.filter(
                        user=request.user, 
                        property_id=property_id
                    ).latest('created_at')
                    
                    # Check if renting has pending/unconfirmed status
                    try:
                        renting_status = MyRentingStatus.objects.filter(renting=user_renting).latest('created_at')
                        
                        # Only return renting if it's NOT confirmed (pending status)
                        if not renting_status.renting_request_confirmed:
                            serializer = self.get_serializer(user_renting)
                            renting_data = serializer.data
                            renting_data['message'] = 'Property is available. Showing pending renting.'
                            renting_data['property_available'] = True
                            renting_data['my_renting_status'] = {
                                'id': renting_status.id,
                                'renting_request_confirmed': renting_status.renting_request_confirmed,
                                'renting_status': renting_status.renting_status,
                                'confirmed_at': renting_status.confirmed_at,
                                'started_at': renting_status.started_at,
                                'canceled_at': renting_status.canceled_at,
                                'created_at': renting_status.created_at,
                                'updated_at': renting_status.updated_at
                            }
                            
                            return Response(renting_data, status=status.HTTP_200_OK)
                            
                    except MyRentingStatus.DoesNotExist:
                        # No renting status means it's pending
                        serializer = self.get_serializer(user_renting)
                        renting_data = serializer.data
                        renting_data['message'] = 'Property is available. Showing pending renting.'
                        renting_data['property_available'] = True
                        renting_data['my_renting_status'] = None  # No status record exists
                        
                        return Response(renting_data, status=status.HTTP_200_OK)
                    
                except MyRenting.DoesNotExist:
                    pass
                    
                # No pending renting found or user has no renting at all
                return Response({
                    'message': 'Property is available. User has no renting or no pending renting.',
                    'property_available': True,
                    'has_renting': False
                }, status=status.HTTP_200_OK)
            
            # Property is not available, check if user has an active renting for this property
            try:
                from .models import MyRentingStatus
                
                # Get user's renting for this property
                user_renting = self.queryset.filter(
                    user=request.user, 
                    property_id=property_id
                ).latest('created_at')
                
                # Check if this renting has an active status
                try:
                    renting_status = MyRentingStatus.objects.filter(renting=user_renting).latest('created_at')
                    
                    # Check if renting is active (confirmed and ongoing)
                    if (renting_status.renting_request_confirmed and 
                        renting_status.renting_status == 'ongoing'):
                        
                        # Check if renting dates are still active (check-out date hasn't passed)
                        from django.utils import timezone
                        
                        current_date = timezone.now().date()
                        
                        if user_renting.check_out >= current_date:
                            # Renting is active
                            serializer = self.get_serializer(user_renting)
                            renting_data = serializer.data
                            renting_data['renting_status'] = 'active'
                            renting_data['property_available'] = False
                            renting_data['my_renting_status'] = {
                                'id': renting_status.id,
                                'renting_request_confirmed': renting_status.renting_request_confirmed,
                                'renting_status': renting_status.renting_status,
                                'confirmed_at': renting_status.confirmed_at,
                                'started_at': renting_status.started_at,
                                'canceled_at': renting_status.canceled_at,
                                'created_at': renting_status.created_at,
                                'updated_at': renting_status.updated_at
                            }
                            
                            return Response(renting_data, status=status.HTTP_200_OK)
                
                except MyRentingStatus.DoesNotExist:
                    pass
                
                # If we reach here, user has renting but it's not active
                return Response({
                    'message': 'Property is not available and you have no active renting.',
                    'property_available': False
                }, status=status.HTTP_200_OK)
                
            except MyRenting.DoesNotExist:
                # User has no renting for this property
                return Response({
                    'message': 'Property is not available and you have no renting for this property.',
                    'property_available': False
                }, status=status.HTTP_200_OK)
                
        except Property.DoesNotExist:
            return Response({
                'message': 'Property not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f'Error retrieving renting: {str(e)}')
            return Response({
                "message": "An error occurred while retrieving renting."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def create(self, request, *args, **kwargs):
        logger = logging.getLogger(__name__)
        user = request.user
        
        property_id = request.data.get('property', None)
        if not property_id:
            return Response({
                'message': 'Property ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if property exists and is available
        try:
            property_obj = Property.objects.get(id=property_id)
            if not property_obj.availability_status:
                return Response({
                    'message': 'Property is not available for renting'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Property.DoesNotExist:
            return Response({
                'message': 'Property not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Regular rental creation - validate all required fields
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
        
        rental_data = {
            'property': property_id,
            'renting_duration': request.data.get('renting_duration'),
            'total_price': total_price,
            'check_in': request.data.get('check_in'),
            'check_out': request.data.get('check_out'),
            'total_family_member': total_family_member,
            'adult': adult,
            'children': children,
            'user': user.id
        }

        serializer = CreateMyRentingSerializer(data=rental_data)
        if serializer.is_valid():
            rental_instance = serializer.save()
            logger.info(f"Rental created successfully with ID: {rental_instance.id}")
            return Response({
                "message": "Renting created successfully",
                "rental_id": rental_instance.id,
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Rental creation failed: {serializer.errors}")
            return Response({
                'message': 'Rental information not added.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST) 

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
            'accountNumber': accountNumber,
            'amount': amount
        }
        
        # Validate provider
        is_valid, error_message = PaymentValidator.validate_provider(payment_method)
        if not is_valid:
            return Response({
                "message": error_message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate phone number
        is_valid, error_message = PaymentValidator.validate_phone_number(accountNumber, payment_method)
        if not is_valid:
            return Response({
                "message": error_message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate amount
        is_valid, error_message, validated_amount = PaymentValidator.validate_amount(amount)
        if not is_valid:
            return Response({
                "message": error_message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update payment data with validated amount
        payment_data['amount'] = validated_amount
        
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
        queryset = self.filter_queryset(self.get_queryset()).filter(user=request.user).order_by('-created_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get the latest rental for the authenticated user"""
        try:
            user = request.user
            latest_rental = MyRenting.objects.filter(user=user).latest('created_at')
            serializer = self.get_serializer(latest_rental)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MyRenting.DoesNotExist:
            return Response({
                'message': 'No rentals found for this user.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def for_duplication(self, request):
        """Get user's previous rentals that can be duplicated"""
        user = request.user
        limit = request.query_params.get('limit', 10)
        
        try:
            limit = int(limit)
            if limit > 50:  # Prevent excessive data retrieval
                limit = 50
        except (ValueError, TypeError):
            limit = 10
            
        # Get user's previous rentals, ordered by most recent
        rentals = MyRenting.objects.filter(user=user).order_by('-created_at')[:limit]
        
        if not rentals.exists():
            return Response({
                'message': 'No previous rentals found for duplication.',
                'data': []
            }, status=status.HTTP_200_OK)
        
        # Create simplified data for duplication selection
        rental_data = []
        for rental in rentals:
            rental_data.append({
                'id': rental.id,
                'property_name': rental.property.name,
                'property_id': rental.property.id,
                'check_in': rental.check_in,
                'check_out': rental.check_out,
                'renting_duration': {
                    'id': rental.renting_duration.id if rental.renting_duration else None,
                    'duration': rental.renting_duration.duration if rental.renting_duration else None
                },
                'total_family_member': rental.total_family_member,
                'total_price': rental.total_price,
                'adult': rental.adult,
                'children': rental.children,
                'created_at': rental.created_at,
                'property_image': rental.property.property_images.first().image.url if rental.property.property_images.exists() else None
            })
        
        return Response({
            'message': 'Previous rentals retrieved successfully.',
            'count': len(rental_data),
            'data': rental_data
        }, status=status.HTTP_200_OK)
    