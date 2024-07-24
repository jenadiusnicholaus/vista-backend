from rest_framework import serializers

from property.models import PropertyHostCancelationPolicy  # Correct import

class PropertyHostCancelationPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyHostCancelationPolicy
        fields = '__all__'  # Adjust fields as necessary