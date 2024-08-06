from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from authentication.models import AzamPayAuthToken



User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "is_active",
            "phone_is_verified",    
            "last_login",
            "date_joined",
            'user_profile_pic',
          
           
        )
        read_only_fields = ("id", "is_staff", "is_active", "date_joined")
       




    



class VGuestRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "password",
            "password2",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "agreed_to_Terms"
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data["phone_number"],
            date_of_birth=validated_data["date_of_birth"],
            agreed_to_Terms=validated_data["agreed_to_Terms"]
               
        )

        user.set_password(validated_data["password"])
        user.is_active = False
        user.is_staff = False
        user.save()

        return user
    
class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()
    token = serializers.CharField()

class AzamPayAuthSerializer(serializers.ModelSerializer):


    class Meta: 
        model = AzamPayAuthToken
        fields = [
            'access_token',
            'refresh_token',
            'token_type',
            'expires_in',
            'created_at',
            'updated_at'
        ]
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }


