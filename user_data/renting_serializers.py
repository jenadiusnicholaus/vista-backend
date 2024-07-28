

from property.models import PropertyRentingDurationOptions
from property.serializers import PropertyRentingDurationOptionsSerializers, PropertySerializers
from user_data.booking_serializers import MyMobileMoneyPaymentinfosSerializers, MyPaymentCardSerializers
from user_data.models import MyMobileMoneyPaymentinfos, MyPaymentCard, MyRenting, MyRentingPayment, MyRentingPaymentStatus, MyRentingStatus
from rest_framework import serializers


class MyRentingStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyRentingStatus
        fields = [
            'id',
            'user',
            'renting',
            'renting_request_confirmed',
            'renting_status',
            'confirmed_at',
            'started_at',
            'canceled_at',
            'created_at',
            'updated_at',
        ]

class CreateMyRentingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyRenting
        # use the above  commented fields
        fields = [
            "user",
            'property',
            'renting_duration',
            'total_price',
            "check_in",
            "check_out",
            "total_family_member",
            "adult",
            "children",
            'created_at',
            'updated_at',
        ]

class MyRentingSerializer(serializers.ModelSerializer):
    my_payment_card = serializers.SerializerMethodField() 
    my_mw_payment = serializers.SerializerMethodField()
    renting_status = serializers.SerializerMethodField()
    renting_duration = PropertyRentingDurationOptionsSerializers()
    property = PropertySerializers()


    class Meta:
        model = MyRenting
        fields = [  
             'id',
            'property',
            'renting_duration',
            'total_price',
            "check_in",
            "check_out",
            "total_family_member",
            "adult",
            "children",
            'created_at',
            'updated_at',
            'my_payment_card',
            'my_mw_payment',
            'renting_status',

        ]
        

        extra_kwargs = {
            'property': {'required': False},
            'renting_duration': {'required': False},
            'renting_price': {'required': False},
            'renting_status': {'required': False},
            'created_at': {'required': False},
            'updated_at': {'required': False},
        }

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
    
    def get_renting_status(self, obj):
        myRentingStatus = None
        
        try:
          myRentingStatus =  MyRentingStatus.objects.filter(renting=obj).latest('created_at')
        except MyRentingStatus.DoesNotExist:
            myRentingStatus = None

        return MyRentingStatusSerializer( myRentingStatus ).data
    

class CreateMyRentingPaymentSerializers(serializers.ModelSerializer):

    class Meta:
        model = MyRentingPayment
        fields =[
            'id',
            'user',
            'renting',
            'payment_method',
            "transaction_id",
            "total_price",
            'created_at',
            'updated_at',
        ]
    


class CreateMyRentingPaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyRentingPaymentStatus
        fields = [
            "user",
            "renting",
            "renting_payment",
            "payment_confirmed",
            "payment_completed",
            "payment_canceled",
            "confirmed_at",
            "completed_at",
            "canceled_at",
            "to_be_refunded",
            "created_at",
            "updated_at",
        ]

class CreateMyRentingStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyRentingStatus
        fields = [
            'id',
            'user',
            'renting',
            'renting_request_confirmed',
            'renting_status',
            'confirmed_at',
            'started_at',
            'canceled_at',
            'created_at',
            'updated_at',
        ]

  

        
        

    



