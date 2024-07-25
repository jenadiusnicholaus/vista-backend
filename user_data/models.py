from django.db import models
from django.contrib.auth import get_user_model
from property.models import Property

User = get_user_model()

class MyFavoriteProperty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '01. My Favorite Property'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'property')


    def __str__(self):
        return f'{self.user.email} - {self.property.name} - {self.property.name}'
    
class MyAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '02. My Address'
        verbose_name_plural = verbose_name  

    def __str__(self):
        return f'{self.user.email} - {self.address} - {self.city} - {self.state} - {self.country}'
    
class MyPaymentCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=100, unique=True)
    bank_name = models.CharField(max_length=100, null=True)
    card_holder_name = models.CharField(max_length=100)
    card_expiry = models.CharField(max_length=100, null=True, blank=True)
    card_cvv = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '03. My Payment Card'
        verbose_name_plural = verbose_name  

    def __str__(self):
        return f'{self.user.email} - {self.account_number} - {self.card_holder_name} - {self.card_expiry} - {self.card_cvv}'

class MyMobileMoneyPaymentinfos(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=100, )
    mobile_holder_name = models.CharField(max_length=100)
    mobile_network = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '04. Mobile Money Payment '
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.email} - {self.mobile_number} - {self.mobile_holder_name} - {self.mobile_network}'
    
#  ===================== Property Booking =====================

class MyBooking(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    total_guest = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    adult = models.IntegerField()
    children = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'property')
        verbose_name = '05. My Booking'   
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.email} - {self.property.name} - {self.check_in} - {self.check_out} - {self.total_guest}'
    
class MyBookingStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.ForeignKey(MyBooking, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)   
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'booking')
        verbose_name = '06. Booking Status'    
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.email} - {self.booking.property.name} - {self.booking.check_in} - {self.booking.check_out} - {self.booking.total_guest}'

class MyBookingPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.ForeignKey(MyBooking, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=100, null=True)
    transaction_id = models.CharField(max_length=100, null=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        unique_together = ('user', 'booking')
        verbose_name = '07. Booking Payment'
        verbose_name_plural = verbose_name


    def __str__(self):
        return f'{self.user.email} - {self.booking.property.name}'
    

    
class MyBookingPaymentStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.ForeignKey(MyBooking, on_delete=models.CASCADE, null=True)

    booking_payment = models.ForeignKey(MyBookingPayment, on_delete=models.CASCADE)
    payment_confirmed = models.BooleanField(default=False)
    payment_completed = models.BooleanField(default=False)
    payment_canceled = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    to_be_refunded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('user', 'booking_payment')
        verbose_name = '08. Booking Payment Status'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.email} - {self.booking_payment.booking.property.name}'  
    
    
# ===================== Property Renting =====================
class MyRenting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    total_family_member = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    adult = models.IntegerField()
    children = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        unique_together = ('user', 'property')
        verbose_name = '09. Renting'
        verbose_name_plural = verbose_name



    def __str__(self):
        return f'{self.user.email} - {self.property.name} - {self.check_in} - {self.check_out} - {self.total_family_member}'


class MyRentingPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    renting = models.ForeignKey(MyRenting, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=100, null=True)   
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'renting')
        verbose_name = '10. Renting Payment'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.email} - {self.renting.property.name} - {self.total_price}'
    
class MyRentingStatus(models.Model):    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    renting = models.ForeignKey(MyRenting, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)   
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'renting') 
        verbose_name = '11. Renting Status'
        verbose_name_plural = verbose_name  


    def __str__(self):
        return f'{self.user.email} - {self.renting.property.name}'
class MyRentingPaymentStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    renting = models.ForeignKey(MyRenting, on_delete=models.CASCADE, null=True)

    renting_payment = models.ForeignKey(MyRentingPayment, on_delete=models.CASCADE)
    payment_confirmed = models.BooleanField(default=False)
    payment_completed = models.BooleanField(default=False)
    payment_canceled = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    to_be_refunded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        unique_together = ('user', 'renting_payment') 
        verbose_name = '12. Payment Status'
        verbose_name_plural = verbose_name  

    def __str__(self):
        return f'{self.user.email} - {self.renting_payment.renting.property.name} '

    
# ===================== Property Purchase =====================
class MyPropertyPurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'property')
        verbose_name = '13. Property Purchase'
        verbose_name_plural = verbose_name


    def __str__(self):
        return f'{self.user.email} - {self.property.name}'
    

class MyPropertyPurchasePayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property_purchase = models.ForeignKey(MyPropertyPurchase, on_delete=models.CASCADE)
    payment_method =     payment_method = models.CharField(max_length=100, null=True)   
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'property_purchase')
        verbose_name = '14. Purchase Payment'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.email} - {self.property_purchase.property.name}'
    
class MyPropertyPurchaseStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property_purchase = models.ForeignKey(MyPropertyPurchase, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'property_purchase')
        verbose_name = '15. Purchase Status'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.email} - {self.property_purchase.property.name} '
    
class MyPropertyPurchasePaymentStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property_purchase = models.ForeignKey(MyPropertyPurchase, on_delete=models.CASCADE, null=True)
    property_purchase_payment = models.ForeignKey(MyPropertyPurchasePayment, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    to_be_refunded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'property_purchase_payment')
        verbose_name = '16. Purchase Payment Status'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.email} - {self.property_purchase_payment.property_purchase.property.name} '
    

