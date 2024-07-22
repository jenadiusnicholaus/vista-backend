from django.contrib import admin
from . models import  (Property, PropertyAmenity,PropertyFacility , PropertyImages, PropertyHost, Category, PropertyReview, SupportedGeoRegions, DeliverGeoRegion,PropertyHostVerification, PropertyHostCancelationPolicy,PropertyRules, PropertyRentingRequirements, PropertyRentingDurationOptions)

class PropertyAdmin(admin.ModelAdmin):
    list_display = [ 'name', 'category', 'price',  'address', 'city', 'state', 'country', 'latitude', 'longitude','host', 'image', 'availability_status', 'publication_status', 'created_at', 'updated_at']
    search_fields = [ 'name', 'category', 'price',  'address', 'city', 'state', 'country', 'latitude', 'longitude','host', 'image', 'availability_status', 'publication_status', 'created_at', 'updated_at']
    list_filter = [ 'name', 'category', 'price',  'address', 'city', 'state', 'country', 'latitude', 'longitude','host', 'image', 'availability_status', 'publication_status', 'created_at', 'updated_at']
    list_per_page = 10

class PropertyAmenityAdmin(admin.ModelAdmin):
    list_display = ['property', 'name']
    search_fields = ['property', 'name']
    list_filter = ['property', 'name']
    list_per_page = 10


class PropertyFacilityAdmin(admin.ModelAdmin):
    list_display = ['property', 'facility']
    search_fields = ['property', 'facility']
    list_filter = ['property', 'facility']
    list_per_page = 10


class PropertyImagesAdmin(admin.ModelAdmin):
    list_display = ['property', 'image']
    search_fields = ['property', 'image']
    list_filter = ['property', 'image']
    list_per_page = 10


class PropertyhostAdmin(admin.ModelAdmin):
    list_display = ['property_count', 'user']
    search_fields = ['property_host', 'user']
    list_filter = ['property_host', 'user']
    list_per_page = 10


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']
    list_filter = ['name', 'description']
    list_per_page = 10
class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = ['property', 'user', 'rating', 'comment']
    search_fields = ['property', 'user', 'rating', 'comment']
    list_filter = ['property', 'user', 'rating', 'comment']

    list_per_page = 10
class SupportedGeoRegionsAdmin(admin.ModelAdmin):
    list_display = ['region_name', 'country', 'lat', 'lon', 'address_code', 'state', 'city', 'created_at', 'updated_at']
    search_fields = ['region_name', 'country', 'lat', 'lon', 'address_code', 'state', 'city', 'created_at', 'updated_at']
    list_filter = ['region_name', 'country', 'lat', 'lon', 'address_code', 'state', 'city', 'created_at', 'updated_at']
    # auto fill the slug
    prepopulated_fields = {'slug': ('region_name',)}
    list_per_page = 10

class DeliverGeoRegionAdmin(admin.ModelAdmin):
    list_display = ['region_name', 'country', 'lat', 'lon', 'address_code', 'state', 'city', 'created_at', 'updated_at']
    search_fields = ['region_name', 'country', 'lat', 'lon', 'address_code', 'state', 'city', 'created_at', 'updated_at']
    list_filter = ['region_name', 'country', 'lat', 'lon', 'address_code', 'state', 'city', 'created_at', 'updated_at']
    # auto fill the slug
    prepopulated_fields = {'slug': ('region_name',)}
    list_per_page = 10

class PropertyRentingDurationOptionsAdmin(admin.ModelAdmin):
    list_display = ['time_in_number', 'time_in_text']
    search_fields = ['time_in_number', 'time_in_text']
    list_filter = ['time_in_number', 'time_in_text']
    list_per_page = 10


admin.site.register(PropertyHostVerification)
admin.site.register(PropertyRentingRequirements)
admin.site.register(PropertyHostCancelationPolicy)
admin.site.register(PropertyRules)  
admin.site.register(PropertyAmenity, PropertyAmenityAdmin)
admin.site.register(PropertyFacility, PropertyFacilityAdmin)
admin.site.register(PropertyImages, PropertyImagesAdmin)
admin.site.register(PropertyHost, PropertyhostAdmin)
admin.site.register(PropertyReview, PropertyReviewAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(SupportedGeoRegions, SupportedGeoRegionsAdmin)
admin.site.register(DeliverGeoRegion, DeliverGeoRegionAdmin)
admin.site.register(PropertyRentingDurationOptions, PropertyRentingDurationOptionsAdmin)





