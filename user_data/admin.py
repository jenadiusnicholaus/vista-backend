from django.contrib import admin
from . models import *


class MyFavoritePropertyAdmin(admin.ModelAdmin):
    list_display = ['user', 'property']
    search_fields = ['user', 'property']
    list_filter = ['user', 'property']
    list_per_page = 10


admin.site.register(MyFavoriteProperty, MyFavoritePropertyAdmin)
admin.site.register(MyAddress)
admin.site.register(MyPaymentCard)
admin.site.register(MyBooking)
admin.site.register(MyBookingPayment)
admin.site.register(MyBookingStatus)
admin.site.register(MyBookingPaymentStatus)
admin.site.register(MyRenting)
admin.site.register(MyRentingPayment)
admin.site.register(MyRentingStatus)
admin.site.register(MyRentingPaymentStatus)
admin.site.register(MyPropertyPurchase)
admin.site.register(MyPropertyPurchasePayment)
admin.site.register(MyPropertyPurchaseStatus)
admin.site.register(MyPropertyPurchasePaymentStatus)



# admin.site.register(MyFavoriteProperty)



