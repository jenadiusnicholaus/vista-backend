from rest_framework import serializers

from fcm.models import FcmNotification, FcmTokenModel
from fcm.serializers import FcmTokenModelSerializer
from user_data.models import MyFavoriteProperty
from .models import Property, PropertyHost, Category, PropertyFacility, PropertyHostCancelationPolicy, PropertyImages, PropertyRentingDurationOptions, PropertyRentingRequirements, PropertyReview, PropertyAmenity, SupportedGeoRegions
from django.contrib.auth import get_user_model
from django.conf import settings 
from authentication.serializers import UserSerializer
from django.db import models   


class GetPropertyhostSerializers(serializers.ModelSerializer):
    user = UserSerializer()
    fcmtoken = serializers.SerializerMethodField()


    class Meta:
        model = PropertyHost
        fields = [
            'id',
            'user',
            'fcmtoken',
            "is_verified",
            "property_count",
            'created_at',
            'updated_at'
        ]

    def get_fcmtoken(self, obj):
        try:
            tokenModel = FcmTokenModel.objects.get(user=obj.user)
            return FcmTokenModelSerializer(tokenModel).data
        except:
            return None

    def get_time_at_visita(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')

class GetCategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PropertyHostCancelationPolicySerializers(serializers.ModelSerializer):
    class Meta:
        model = PropertyHostCancelationPolicy
        fields = '__all__'

class PropertyRentingRequirementsSerializers(serializers.ModelSerializer):
    class Meta:
        model = PropertyRentingRequirements
        fields = '__all__'


class PropertyRentingDurationOptionsSerializers(serializers.ModelSerializer):
    class Meta:
        model = PropertyRentingDurationOptions
        fields = '__all__'
   

class PropertySerializers(serializers.ModelSerializer):
    host = GetPropertyhostSerializers()
    category = GetCategorySerializers()
    is_my_favorite = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    BORpolicy = serializers.SerializerMethodField()
    prrs = serializers.SerializerMethodField()
    rdos = serializers.SerializerMethodField()
    # booking_status = serializers.SerializerMethodField()



    class Meta:
        model = Property
        fields = [
            'id',
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
            'host',
            'availability_status',
            'publication_status',
            'created_at',
            'updated_at',
            'is_my_favorite',
            'business_type',
            'rating',
            "supported_geo_region",
            "contract_draft",
            "BORpolicy",
            "prrs",
            "rdos"
        ]
        extra_kwargs = {
            'image': {'required': False},
            'availability_status': {'required': False},
            'publication_status': {'required': False},
        }
        read_only_fields = ['host', 'created_at', 'updated_at']

    def get_is_my_favorite(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return MyFavoriteProperty.objects.filter(user=user, property=obj).exists()
 
        return False
    
    def get_rating(self, obj):
        reviews = PropertyReview.objects.filter(property=obj)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0.0  

    def get_BORpolicy(self, obj):
        try:
            return PropertyHostCancelationPolicySerializers(obj.cancelation_policy).data    
        except:
            return None
        
    def get_prrs(self, obj):
        try:
            return PropertyRentingRequirementsSerializers(obj.renting_requirements.all(),many = True).data    
        except:
            return None
        
    def get_rdos(self, obj):
        try:
            return PropertyRentingDurationOptionsSerializers(obj.renting_duration_options.all(),many = True).data    
        except:
            return None
        
   
        

class GetPropertyFacilitySerializers(serializers.ModelSerializer):
    class Meta:
        model = PropertyFacility
        fields = '__all__'

class PropertyImagesSerializers(serializers.ModelSerializer):   
    class Meta:
        model = PropertyImages
        fields = '__all__'

class PropertyReviewSerializers(serializers.ModelSerializer): 
    user = UserSerializer()
    class Meta:
        model = PropertyReview
        fields = '__all__'
class CreatePropertyReviewSerializers(serializers.ModelSerializer):
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
    host = GetPropertyhostSerializers() 
    category = GetCategorySerializers()
    

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
            'host',
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
        read_only_fields = ['host', 'created_at', 'updated_at', 'images', 'facilities', 'reviews', 'amenities']

class SupportedGeoRegionsSerializers(serializers.ModelSerializer):
    total_properties = serializers.SerializerMethodField()



    class Meta:
        model = SupportedGeoRegions
        fields = [
            'id',
            'region_name',
            'is_country',
            'image',
            'is_published',
            'slug',
            'country',
            'lat',
            'lon',
            'address_code',
            'state',
            'city',
            'created_at',
            'updated_at',
            'total_properties'
        ]

    def get_total_properties(self, obj):
        return Property.objects.filter(supported_geo_region=obj).count()

    

  