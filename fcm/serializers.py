from fcm.models import FcmNotification, FcmTokenModel
from rest_framework import serializers


class FcmNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FcmNotification
        fields = [
            'user',
            'title',
            'body',
            'data',
            'created_at',
            'updated_at'    
        ]
        read_only_fields = ('created_at', 'updated_at') 
        extra_kwargs = {
            'title': {'required': True},
            'body': {'required': True},
            'data': {'required': True}
        }   

class FcmTokenModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FcmTokenModel
        fields = [
            'user',
            'fcm_token',
            'time_stamp',   
            'is_stale',
            'stale_time'
        ]
        read_only_fields = ('time_stamp', 'stale_time')
        extra_kwargs = {
            'fcm_token': {'required': True},
            'stale_time': {'required': True},
            'time_stamp': {'required': False},
            'is_stale': {'required': False} 
     }
#
        
        
   