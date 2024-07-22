from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from authentication.serializers import UserSerializer
from property.serializers import PropertySerializers
from user_data.models import MyFavoriteProperty

User = get_user_model()




class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)  # Assuming you want to include email

    class Meta:
        model = User
        fields = ["first_name", "last_name", "user_profile_pic", "email", "phone_number"]
        read_only_fields = ['user_profile_pic']

    def validate_email(self, value):
        # Check if the email is being updated to a value that already exists
        if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        # Assuming you want to conditionally update the email if it's included
        if 'email' in validated_data:
            instance.email = validated_data.get('email')
        # Handle user_profile_pic if it's not meant to be read-only or is conditionally updated
        instance.save()
        return instance
    
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

      