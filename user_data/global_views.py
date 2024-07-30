from django.contrib.auth import get_user_model
from rest_framework import viewsets, status 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from property.paginators import CustomPageNumberPagination
from user_data.global_serializers import CreateMyFavoritePropertySerializers, GetMyFavoritePropertySerializers, UserProfileSerializer
from user_data.models import MyAddress,  MyFavoriteProperty, MyMobileMoneyPaymentinfos
from user_data.booking_serializers import   MyAddressSerializers,   MyMobileMoneyPaymentinfosSerializers
import logging  as logger 

User = get_user_model()

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
  

    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            serializser = self.get_serializer(user)
            return Response(serializser.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:  
            logger.error('UserProfile does not exist.')  
            return Response({'message': 'UserProfile does not exist.'}, status=status.HTTP_400_BAD_REQUEST) 


    def put(self, request):
        user = request.user
        first_name = request.data.get('first_name', user.first_name)
        second_name = request.data.get('last_name', user.last_name)
        user_profile_pic = request.data.get('user_profile_pic', user.user_profile_pic)  

        data = {
            'first_name': first_name,
            'last_name': second_name,
            'user_profile_pic': user_profile_pic,
            "email": request.data.get('email', user.email)
        }

        serializer = self.get_serializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'User profile updated successfully.',
                'data': serializer.data 
                 },  
                 status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class MyFavoritePropertyViewsSet(viewsets.ModelViewSet):
    queryset = MyFavoriteProperty.objects.all()
    serializer_class = GetMyFavoritePropertySerializers     
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = MyFavoriteProperty.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data) 
    


    def create(self, request, *args, **kwargs): 
        user = request.user
        property_id = request.query_params.get('property_id', None)
        serializers = CreateMyFavoritePropertySerializers(data={
            'user': user.id,
            'property': property_id
        })
        
        if serializers.is_valid():
            serializers.save()
            return Response(
                {
                    'message': 'Property added to favorite successfully.',
                }, status=status.HTTP_201_CREATED)
        else: 
            
            return Response(
                {
                    'message': 'Property not added to favorite.',
                    'data': serializers.errors
                },
                 status=status.HTTP_400_BAD_REQUEST)
        

class MyMobileMoneyPaymentinfosViewSet(viewsets.ModelViewSet):
    queryset = MyMobileMoneyPaymentinfos.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = MyMobileMoneyPaymentinfosSerializers

    def create(self, request, *args, **kwargs):
        user = request.user
        mobile_money_number = request.data.get('mobile_money_number', None)
        mobile_money_name = request.data.get('mobile_money_name', None)
        mobile_money_network = request.data.get('mobile_money_network', None)

        serializers = self.get_serializer(data={
                    'user': user.id,
                    'mobile_number': mobile_money_number,
                    'mobile_holder_name':  user.first_name + ' ' + user.last_name,
                    'mobile_network': mobile_money_network
                })
        if serializers.is_valid():
            serializers.save()
            return Response(
                {
                    'message': 'Mobile money payment details added successfully.',
                }, status=status.HTTP_201_CREATED)

        else:
            return Response(
                {
                    'message': 'Mobile money payment details not added.',
                    'data': serializers.errors
                },
                 status=status.HTTP_400_BAD_REQUEST)  


    
    def patch(self, request, *args, **kwargs):
        try:
            # Assuming you get mobile_money_id from somewhere, e.g., from the request
            mobile_money_id = request.query_params.get('mobile_money_id', None)
            mobile_money_info = MyMobileMoneyPaymentinfos.objects.get(id=mobile_money_id)
            mobile_money_number = request.data.get('mobile_money_number', None)
            mobile_money_name = request.data.get('mobile_money_name', None)
            mobile_money_network = request.data.get('mobile_money_network', None)
            user = request.user
            
            if request.user == mobile_money_info.user:  # Assuming the mobile money has a user field for authorization
                serializer = self.get_serializer(mobile_money_info, data={
                    'mobile_number': mobile_money_number,
                    'mobile_holder_name':  user.first_name + ' ' + user.last_name,
                    'mobile_network': mobile_money_network
                }, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'message': 'Mobile money payment details updated successfully.'}, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'You are not authorized to update this mobile money payment details.'}, status=status.HTTP_403_FORBIDDEN)
        except MyMobileMoneyPaymentinfos.DoesNotExist:
            return Response({'message': 'Mobile money payment   details not found.'}, status=status.HTTP_404_NOT_FOUND)  
        
class MyAddressViewSet(viewsets.ModelViewSet):
    queryset = MyAddress.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = MyAddressSerializers


    def create(self, request, *args, **kwargs):
        user = request.user
        address = request.data.get('address', None)
        city = request.data.get('city', None)
        state = request.data.get('state', None)
        country = request.data.get('country', None)
        latitude = request.data.get('latitude', None)
        longitude = request.data.get('longitude', None)

        serializers = self.get_serializer(data={
                    'user': user.id,
                    'address': address,
                    'city': city,
                    'state': state,
                    'country': country,
                    'latitude': latitude,
                    'longitude': longitude
                })
        if serializers.is_valid():
            serializers.save()
            return Response(
                {
                    'message': 'Address added successfully.',
                }, status=status.HTTP_201_CREATED)

        else:
            return Response(
                {
                    'message': 'Address not added.',
                    'data': serializers.errors
                },
                 status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request, *args, **kwargs):
        try:
            # Assuming you get address_id from somewhere, e.g., from the request
            address_id = request.query_params.get('address_id', None)
            address_info = MyAddress.objects.get(id=address_id)
            address = request.data.get('address', None)
            city = request.data.get('city', None)
            state = request.data.get('state', None)
            country = request.data.get('country', None)
            latitude = request.data.get('latitude', None)
            longitude = request.data.get('longitude', None)
            
            if request.user == address_info.user:  # Assuming the address has a user field for authorization
                serializer = self.get_serializer(address_info, data={
                    'address': address,
                    'city': city,
                    'state': state,
                    'country': country,
                    'latitude': latitude,
                    'longitude': longitude
                }, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'message': 'Address updated successfully.'}, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'You are not authorized to update this address.'}, status=status.HTTP_403_FORBIDDEN)
        except MyAddress.DoesNotExist:
            return Response({'message': 'Address not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': 'An error occurred.', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



            





        




      
        


    
        
  