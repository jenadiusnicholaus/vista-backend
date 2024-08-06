from rest_framework import serializers
from authentication.serializers import UserSerializer
from fcm.serializers import FcmTokenModelSerializer
from property.models import Property
from django.contrib.auth import get_user_model

from property.serializers import PropertySerializers
from user_data.models import MyAddress, MyFavoriteProperty, MyMobileMoneyPaymentinfos, MyPaymentCard

User = get_user_model()
\

class GetMyFavoritePropertySerializers(serializers.ModelSerializer):
    user = UserSerializer()
    property = PropertySerializers()

    class Meta:
        model = MyFavoriteProperty
        fields = '__all__'

class CreateMyFavoritePropertySerializers(serializers.ModelSerializer):
    class Meta:
        model = MyFavoriteProperty
        fields = '__all__'

class MyAddressSerializers(serializers.ModelSerializer):
    class Meta:
        model = MyAddress
        fields = '__all__'

class MyPaymentCardSerializers(serializers.ModelSerializer):
  
    class Meta:
        model = MyPaymentCard
        fields = [
            'id',   
            'account_number',
            'bank_name',
            'card_holder_name',
            'card_expiry',
            'card_cvv',
            'created_at',
            'updated_at',
            'user'
        ]

        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            # not required  
            'card_cvv': {'required': False},
            'card_expiry': {'required': False},
          
        }

class MyMobileMoneyPaymentinfosSerializers(serializers.ModelSerializer):
 
    class Meta:
        model = MyMobileMoneyPaymentinfos
        fields = [
            'id',
            'mobile_number',
            'mobile_holder_name',
            'mobile_network',
            'created_at',
            'updated_at',
            'user'

            
        ]

        extra_kwargs = {    
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            # not required  
            'mobile_holder_name': {'required': False},
            'mobile_network': {'required': False},
        }



class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)  # Assuming you want to include email
    fcm_token = serializers.SerializerMethodField()


    class Meta:
        model = User
        fields = ["first_name", "last_name", "user_profile_pic", "email", "phone_number", "phone_is_verified", "fcm_token"]
        read_only_fields = ['user_profile_pic']

    def get_fcm_token(self, obj):
        try:
            fcm_token = obj.fcm_tokens
            return FcmTokenModelSerializer(fcm_token).data
        except:
            return None



        
      



class PropertyStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['availability_status']