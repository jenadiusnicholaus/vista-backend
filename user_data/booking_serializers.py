from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from authentication.serializers import UserSerializer
from property.serializers import PropertySerializers
from user_data.models import MyAddress, MyBooking, MyBookingPayment, MyBookingPaymentStatus, MyBookingStatus, MyFavoriteProperty, MyMobileMoneyPaymentinfos, MyPaymentCard

User = get_user_model()




class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)  # Assuming you want to include email

    class Meta:
        model = User
        fields = ["first_name", "last_name", "user_profile_pic", "email", "phone_number", "phone_is_verified"]
        read_only_fields = ['user_profile_pic']

   
    
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

class CreateMyBookingSerializers(serializers.ModelSerializer):
    class Meta:
        model = MyBooking
        fields = [
            "id",
            "user",
            'check_in',
            "property",
            'check_out',
            'total_guest',
            'total_price',
            'adult',
            'children',
            'created_at',
            'updated_at'
        ]

        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True}
        }

    


class GetMyBookingSerializers(serializers.ModelSerializer):
    my_address = serializers.SerializerMethodField()
    my_payment_card = serializers.SerializerMethodField() 
    my_mw_payment = serializers.SerializerMethodField()
    my_booking_status = serializers.SerializerMethodField()  
    property =  PropertySerializers() 

    class Meta:
        model = MyBooking
        fields = [
            "id",
            'check_in',
            'check_out',
            'total_guest',
            'total_price',
            'adult',
            'children',
            'my_address',
            'my_payment_card',
            'my_mw_payment',
            'my_booking_status', 
            "property"       
             
        ]

        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True}
        }

    def get_my_address(self, obj):
        # get address where user = logined user  if exist
        address= None 

        try:
            address = MyAddress.objects.filter(user=self.context['request'].user).latest('created_at') 
        except MyAddress.DoesNotExist:
            address = None

        # if address is None:
        #     return None 

        return MyAddressSerializers( address ).data
    
    def get_my_payment_card(self, obj):
        # get address where user = logined user  if exist
        payment_card= None 

        try:
            payment_card = MyPaymentCard.objects.filter(user=self.context['request'].user).latest('created_at') 
        except MyPaymentCard.DoesNotExist:
            payment_card = None

        # if payment_card is None:
        #     return None 

        return MyPaymentCardSerializers( payment_card ).data 

    def get_my_mw_payment(self, obj):
        # get address where user = logined user  if exist
        mobile_money_payment= None 

        try:
            mobile_money_payment = MyMobileMoneyPaymentinfos.objects.filter(user=self.context['request'].user).latest('created_at') 
        except MyMobileMoneyPaymentinfos.DoesNotExist:
            mobile_money_payment = None

        # if mobile_money_payment is None:
        #     return None 

        return MyMobileMoneyPaymentinfosSerializers( mobile_money_payment ).data 
    
    def get_my_booking_status(self, obj):
        # get address where user = logined user  if exist
        booking_status= None 

        try:
            booking_status = MyBookingStatus.objects.filter(user=self.context['request'].user).latest('created_at') 
        except MyBookingStatus.DoesNotExist:
            booking_status = None

        # if booking_status is None:
        #     return None 

        return MyBookingStatusSerializers( booking_status ).data
    



# =============== // user for saving booing information=============
class MyBookingPaymentSerializers(serializers.ModelSerializer):
    class Meta:
        model = MyBookingPayment
        fields = [
            "id",
            'user',
            'booking',
            'payment_method',
            'transaction_id',
            'created_at',
            'updated_at'
        ]

        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True}
        }

    

class MyBookingPaymentStatusSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = MyBookingPaymentStatus
        fields = [
            "id",
            'user',
            "booking",
            'booking_payment',
            'payment_confirmed',
            'payment_completed',
            'payment_canceled',
            'confirmed_at',
            'completed_at',
            'canceled_at',
            'to_be_refunded',
            'created_at',
            'updated_at'
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'payment_confirmed': {'required': True}
        }
        
    
class MyBookingStatusSerializers(serializers.ModelSerializer):

  
    class Meta:
        model = MyBookingStatus
        fields = [
            "id",
            'user',
            'booking',
            'confirmed',
            'completed',
            'canceled',
            'confirmed_at',
            'completed_at',
            'canceled_at',
            'created_at',
            'updated_at'
        ]

        extra_kwargs = {
            'id': {'read_only': True},
            'status': {'required': True}
        } 

    # ================ end =======================

# =============== // user for getting booking information=============

class GetMyBookingDetailsSerializers(serializers.ModelSerializer):
    class Meta:
        model = MyBooking
        fields = [
            "id",
            'check_in',
            "property",
            'check_out',    
            'total_guest',
            'total_price',  
            'adult',
            'children',
            'created_at',
            'updated_at'    
        ]


class GetMyBookingPaymentSerializers(serializers.ModelSerializer):
    booking_payment_status = serializers.SerializerMethodField()
   
    class Meta:
        model = MyBookingPayment
        fields = [
            "id",
            'booking',
            'payment_method',
            'transaction_id',
            'created_at',
            'updated_at',
            'booking_payment_status'
        ]   

    def get_booking_payment_status(self, obj):
        # get address where user = logined user  if exist
        booking_payment_status= None 

        try:
            booking_payment_status = MyBookingPaymentStatus.objects.filter(booking_payment__id = obj.id).latest('created_at') 
        except MyBookingPaymentStatus.DoesNotExist:
            booking_payment_status = None

        # if booking_payment_status is None:
        #     return None 

        return MyBookingPaymentStatusSerializers( booking_payment_status ).data

  

class GetMyBookingStatusSerializers(serializers.ModelSerializer):
    user = UserSerializer()
    booking =GetMyBookingDetailsSerializers()
    booking_payment = serializers.SerializerMethodField()
   
    class Meta:
        model = MyBookingStatus
        fields = [
            "id",
            'user',
            'booking',
            'confirmed',
            'completed',
            'canceled',
            'confirmed_at',
            'completed_at',
            'canceled_at',
            'created_at',
            'updated_at',
            'booking_payment'   
        ]

    def get_booking_payment(self, obj):
        # get address where user = logined user  if exist
        booking_payment= None 

        try:
            booking_payment = MyBookingPayment.objects.filter(user=self.context['request'].user).latest('created_at') 
        except MyBookingPayment.DoesNotExist:
            booking_payment = None

        # if booking_payment is None:
        #     return None 

        return GetMyBookingPaymentSerializers( booking_payment ).data
    
# =============== END=============

        

      