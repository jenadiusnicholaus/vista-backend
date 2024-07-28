from rest_framework import serializers
from property.models import Property



class PropertyStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['availability_status']