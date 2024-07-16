from rest_framework import serializers
from property.models import Property, PropertyOwner, Category, PropertyFacility, PropertyImages, PropertyReview, PropertyAmenity
from django.contrib.auth import get_user_model
from django.conf import settings 


class GetPropertyOwnerSerializers(serializers.ModelSerializer):
    class Meta:
        model = PropertyOwner
        fields = '__all__'

class GetCategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class PropertySerializers(serializers.ModelSerializer):
    owner = GetPropertyOwnerSerializers()
    category = GetCategorySerializers()

    class Meta:
        model = Property
        fields = '__all__'

class GetPropertyFacilitySerializers(serializers.ModelSerializer):
    class Meta:
        model = PropertyFacility
        fields = '__all__'

class PropertyImagesSerializers(serializers.ModelSerializer):   
    class Meta:
        model = PropertyImages
        fields = '__all__'

class PropertyReviewSerializers(serializers.ModelSerializer):   
    class Meta:
        model = PropertyReview
        fields = '__all__'

class PropertyAmenitySerializers(serializers.ModelSerializer):
    class Meta:
        model = PropertyAmenity
        fields = '__all__'



class GetPropertyDetailsSerializers(serializers.ModelSerializer):
    images = PropertyImagesSerializers(many=True)
    facilities = GetPropertyFacilitySerializers(many=True)
    reviews = PropertyReviewSerializers(many=True)
    amenities = PropertyAmenitySerializers(many=True)   

    class Meta:
        model = Property
        fields = [
            'name',
            'category',
            'price',
            'currency',
            'period',   
            'description',
            'address',
            'city',
            'state',
            'country',
            'latitude',
            'longitude',
            'image',
            'owner',
            'availability_status',
            'publication_status',
            'images',
            'facilities',
            'reviews',
            'amenities',
            'created_at',
            'updated_at',
        ]
        extra_kwargs = {
            'image': {'required': False},
            'availability_status': {'required': False},
            'publication_status': {'required': False},
        }
        read_only_fields = ['owner']

  