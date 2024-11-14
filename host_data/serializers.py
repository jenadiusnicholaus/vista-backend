from rest_framework import serializers

from fcm.models import FcmNotification
from property.models import Property, PropertyAmenity, PropertyFacility, PropertyHostCancelationPolicy, PropertyImages, PropertyRentingRequirements, PropertyRules  # Correct import

class PropertyHostCancelationPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyHostCancelationPolicy
        fields = '__all__'  # Adjust fields as necessary

class HostPropertySerializers(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'

class PropertyRulesSerializers(serializers.ModelSerializer):
    class Meta:
        model = PropertyRules
        fields = '__all__'

class PropertyImagesSerializers(serializers.ModelSerializer):
    class Meta:
        model = PropertyImages
        fields = '__all__'

class PropertyFacilitiesSerializers(serializers.ModelSerializer):
    class Meta:
        model = PropertyFacility
        fields = '__all__'

class PropertyAmenitiesSerializers(serializers.ModelSerializer):
    class Meta:
        model = PropertyAmenity
        fields = '__all__'

class PropertyRentingRequirementsSerializers(serializers.ModelSerializer):
    class Meta:
        model = PropertyRentingRequirements
        fields = '__all__'


