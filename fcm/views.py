import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from fcm.google_firebase_service.push_notification.auth_api import GoogleAuth
from fcm.google_firebase_service.push_notification.fcm_api import FCM
from fcm.models import FcmNotification, FcmTokenModel
from fcm.serializers import FcmNotificationSerializer, FcmTokenModelSerializer
from vasta_settings import settings as settings
from rest_framework.permissions import AllowAny

class SendFcmNotification(viewsets.ModelViewSet):
    queryset = FcmNotification.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = FcmNotificationSerializer

    def create(self, request):
        project_id = 'vista-9e65c'
        data = request.data
        title = data.get('title')
        body = data.get('body')
        token = data.get('device_registration_token')
        data = data.get('data')
        exchange_payload = data.get('exchange_payload')
        try:
            google_auth = GoogleAuth(project_id)
            access_token = google_auth.get_access_token()

        except Exception as e:
            logging.error(f'Error: {e}')
            return Response({
                'status': 'error',
                'error': f'{e}',
                'message': 'Error occurred while authenticating google cloud platform'
            },
            status=500)

        try:
            fcm = FCM(project_id, access_token)
        except Exception as e:
            return Response({
                'status': 'error',
                'error': f'{e}',
                'message': 'Error occurred while sending notification'
            },
            status=500) 

        serializers = self.get_serializer(data={
            'user': request.user.id,    
            'title': title,
            'body': body,
            'data': data,

            
        })

        if not serializers.is_valid():
            return Response(serializers.errors, status=400)
        
        status_code, response = fcm.send_notification(
            device_registration_token=token,
            title=title,
            body=body,
            data=data)
        if status_code == 200:
            serializers.save()
            return Response({
                'status': 'success',
                'message': 'Notification sent successfully'
            },
            status=status_code)
        else:
            return Response(response, status=status_code) 
        

class FcmTokenViewSet(viewsets.ModelViewSet):
    queryset = FcmTokenModel.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = FcmTokenModelSerializer

    def list(self, request):
        user = request.user
        try:
            token = FcmTokenModel.objects.get(user=user)
        except FcmTokenModel.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Token does not exist'
            },
            status=404)
        token = FcmTokenModel.objects.get(user=user)
        serializer = self.get_serializer(token)
        return Response(serializer.data, status=200)    

    def create(self, request):
        data = request.data
        token = data.get('fcm_token')
        user = request.user
        serializer = self.get_serializer(data={
            'user': user.id,
            'fcm_token': token
        })
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save()
        return Response({
            'status': 'success',
            'message': 'Token saved successfully'
        },
        status=200)
    
    def patch(self, request):
        data = request.data
        token = data.get('fcm_token')
        user = request.user
        token_instance = FcmTokenModel.objects.get(user=user)
        data = {
            'user': user.id,
            'fcm_token': token,
            "is_stale": False,
        }
        instance = self.get_serializer(token_instance, data=data, partial=True)

        if not instance.is_valid():
            return Response(instance.errors, status=400)
        instance.save()
        return Response({
            'status': 'success',
            'message': 'Token updated successfully'
        },
        status=200)
    


        

