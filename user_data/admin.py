# from django.contrib import admin
# from . models import *


# class MyFavoritePropertyAdmin(admin.ModelAdmin):
#     list_display = ['user', 'property']
#     search_fields = ['user', 'property']
#     list_filter = ['user', 'property']
#     list_per_page = 10


# admin.site.register(MyFavoriteProperty, MyFavoritePropertyAdmin)
# admin.site.register(MyAddress)
# admin.site.register(MyPaymentCard)
# admin.site.register(MyBooking)
# admin.site.register(MyBookingPayment)
# admin.site.register(MyBookingStatus)
# admin.site.register(MyBookingPaymentStatus)
# admin.site.register(MyRenting)
# admin.site.register(MyRentingPayment)
# admin.site.register(MyRentingStatus)
# admin.site.register(MyRentingPaymentStatus)
# admin.site.register(MyPropertyPurchase)
# admin.site.register(MyPropertyPurchasePayment)
# admin.site.register(MyPropertyPurchaseStatus)
# admin.site.register(MyPropertyPurchasePaymentStatus)
# admin.site.register(MyMobileMoneyPaymentinfos)



# # admin.site.register(MyFavoriteProperty)

from django.contrib import admin
from .models import *

class MyFavoritePropertyAdmin(admin.ModelAdmin):
    list_display = ['user', 'property']
    search_fields = ['user', 'property']
    list_filter = ['user', 'property']
    list_per_page = 10

class MyBookingStatusInline(admin.TabularInline):
    model = MyBookingStatus
    extra = 1

class MyBookingPaymentInline(admin.TabularInline):
    model = MyBookingPayment
    extra = 1

class MyBookingPaymentStatusInline(admin.TabularInline):
    model = MyBookingPaymentStatus
    extra = 1

@admin.register(MyBooking)
class MyBookingAdmin(admin.ModelAdmin):
    inlines = [MyBookingStatusInline, MyBookingPaymentInline, MyBookingPaymentStatusInline]
    list_display = ('user', 'property', 'check_in', 'check_out', 'total_guest', 'total_price')
    search_fields = ('user__email', 'property__name')
    list_filter = ('check_in', 'check_out')

class MyRentingPaymentInline(admin.TabularInline):
    model = MyRentingPayment
    extra = 1

class MyRentingStatusInline(admin.TabularInline):
    model = MyRentingStatus
    extra = 1

class MyRentingPaymentStatusInline(admin.TabularInline):
    model = MyRentingPaymentStatus
    extra = 1

@admin.register(MyRenting)
class MyRentingAdmin(admin.ModelAdmin):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    # property = models.ForeignKey(Property, on_delete=models.CASCADE)
    # check_in = models.DateField()
    # check_out = models.DateField()
    # total_family_member = models.IntegerField()
    # total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # adult = models.IntegerField()
    # children = models.IntegerField()
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    inlines = [MyRentingPaymentInline, MyRentingStatusInline, MyRentingPaymentStatusInline]
    list_display = ('user', 'property', 'check_in', 'check_out', 'total_family_member', 'total_price')
    search_fields = ('user__email', 'property__name')
    list_filter = ('check_in', 'check_out')

class MyPropertyPurchasePaymentInline(admin.TabularInline):
    model = MyPropertyPurchasePayment
    extra = 1

class MyPropertyPurchaseStatusInline(admin.TabularInline):
    model = MyPropertyPurchaseStatus
    extra = 1

class MyPropertyPurchasePaymentStatusInline(admin.TabularInline):
    model = MyPropertyPurchasePaymentStatus
    extra = 1

@admin.register(MyPropertyPurchase)
class MyPropertyPurchaseAdmin(admin.ModelAdmin):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    # property = models.ForeignKey(Property, on_delete=models.CASCADE)
    # total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    inlines = [MyPropertyPurchasePaymentInline, MyPropertyPurchaseStatusInline, MyPropertyPurchasePaymentStatusInline]
    # list_display = ('user', 'property', 'purchase_date', 'total_price')
    # search_fields = ('user__email', 'property__name')
    # list_filter = ('purchase_date',)
    list_display = ('user', 'property', 'total_price')
    search_fields = ('user__email', 'property__name')
  




admin.site.register(MyFavoriteProperty, MyFavoritePropertyAdmin)
admin.site.register(MyAddress)
admin.site.register(MyPaymentCard)
# admin.site.register(MyBookingPayment)
# admin.site.register(MyBookingStatus)
# admin.site.register(MyBookingPaymentStatus)
# # admin.site.register(MyRenting, MyRentingAdmin)
# admin.site.register(MyRentingPayment)
# admin.site.register(MyRentingStatus)
# admin.site.register(MyRentingPaymentStatus)
# # admin.site.register(MyPropertyPurchase, MyPropertyPurchaseAdmin)
# admin.site.register(MyPropertyPurchasePayment)
# admin.site.register(MyPropertyPurchaseStatus)
# admin.site.register(MyPropertyPurchasePaymentStatus)
admin.site.register(MyMobileMoneyPaymentinfos)


