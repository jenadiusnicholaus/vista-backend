from django.contrib.auth import get_user_model
from rest_framework import viewsets, status 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from property.paginators import CustomPageNumberPagination
from user_data.models import MyFavoriteProperty
from user_data.serializers import CreateMyFavoritePropertySerializers, GetMyFavoritePropertySerializers, UserProfileSerializer
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


       

        
