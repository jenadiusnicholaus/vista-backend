from rest_framework import serializers

from fcm.models import FcmNotification
from property.models import PropertyHostCancelationPolicy  # Correct import

class PropertyHostCancelationPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyHostCancelationPolicy
        fields = '__all__'  # Adjust fields as necessary

# class FcmNotificationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FcmNotification
#         fields = [
#             'user',
#             'title',
#             'body',
#             'data',
#             'created_at',
#             'updated_at'    
#         ]
#         read_only_fields = ('created_at', 'updated_at') 
#         extra_kwargs = {
#             'title': {'required': True},
#             'body': {'required': True},
#             'data': {'required': True}
#         }     