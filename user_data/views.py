from django.contrib.auth import get_user_model
from rest_framework import viewsets, status 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from user_data.serializers import UserProfileSerializer
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
           




        
