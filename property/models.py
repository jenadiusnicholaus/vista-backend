from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

from host_data.models import PropertyHost



User = get_user_model()


# // category model
class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        verbose_name = '01. Category'   
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
    
  
class SupportedGeoRegions(models.Model):
    region_name = models.CharField(max_length=100, unique=True)
    is_country = models.BooleanField(default=False)
    image = models.ImageField(upload_to='geo_region_images/', null=True, blank=True)    
    is_published = models.BooleanField(default=True)
    slug = models.SlugField(max_length=100, unique=True)
    country = models.CharField(max_length=100)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lon = models.DecimalField(max_digits=9, decimal_places=6)
    address_code = models.CharField(max_length=100)                  
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '02. Supported Geo Region'   
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.region_name
    
class DeliverGeoRegion(models.Model):
    region_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    country = models.CharField(max_length=100)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lon = models.DecimalField(max_digits=9, decimal_places=6)
    address_code = models.CharField(max_length=100)                  
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '03. Deliver Geo Region'   
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.region_name
    
   
# create very details models for the property app 
class Property(models.Model):
    AVAILABILITY_STATUS=(
        (True, 'Available'),
        (False, 'Not Available')
    )
    PUBLICATION_STATUS=(
        (True, 'Published'),
        (False, 'Not Published')
    )

    period=(
        ('night', 'Night'),
        ('minute', 'Minute'),   
        ('hour', 'Hour'),
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('year', 'Year')
        ) 
    CURRENCY = (
        ('Tsh', 'Tsh'),
        ('USD', 'USD'),
        ('Ksh', 'Ksh'),
        ('EUR', 'EUR'),
    )

    business_type = (
        ('rent', 'Rent'),
        ('sale', 'Sale'),
        ('booking', 'Booking'),
    )


    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    currency = models.CharField(max_length=10, choices=CURRENCY, default='Tsh' ) 
    period = models.CharField(max_length=10, choices=period, null = True)
    description = models.TextField()
    address = models.CharField(max_length=100)
    supported_geo_region = models.ForeignKey(SupportedGeoRegions, on_delete=models.CASCADE, related_name='supported_geo_region', null=True)
    business_type = models.CharField(choices=business_type, max_length=100, null = True) 
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)  
    longitude = models.DecimalField(max_digits=9, decimal_places=6)  
    image = models.ImageField(upload_to='property_pics/', null=True, blank=True)  
    host = models.ForeignKey(PropertyHost, on_delete=models.CASCADE, related_name='property_host', null=True)
    availability_status = models.BooleanField(default=True, choices=AVAILABILITY_STATUS )
    publication_status = models.BooleanField(default=True, choices=PUBLICATION_STATUS)
    contract_draft =  models.FileField(upload_to='contract_draft/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        verbose_name = '04. Properties'   
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
    
class PropertyHostCancelationPolicy(models.Model):
    # property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='cancelation_policy')
    # host = models.ForeignKey(PropertyHost, on_delete=models.CASCADE, related_name='host_cancelation_policy')
    title = models.CharField(max_length=100, null=True, blank=True) 
    policy = models.TextField()
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '05. Cancelation Policy'   
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title   
    
class PropertyRules(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='renting_rules')
    rule = models.CharField(max_length=100) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '06. Property Rules'   
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.property.name
    
class PropertyRentingRequirements(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='renting_requirements')
    requirement = models.CharField(max_length=100) 
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '07. Renting Requirements'   
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.property.name
    
 
class PropertyImages(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property_pics/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        verbose_name = '08. Property Images'   
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.property.name
    
class PropertyFacility(models.Model):
    property = models.ForeignKey(Property, related_name='facilities', on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    facility = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = '09. Property Facility'   
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.facility
    
class PropertyAmenity(models.Model):
    property = models.ForeignKey(Property, related_name='amenities', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '10. Property Amenity'   
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
    
class PropertyReview(models.Model):
    property = models.ForeignKey(Property, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField()
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)



    class Meta:
        unique_together = ('property', 'user')
        verbose_name = '11. Property Review'
        verbose_name_plural = verbose_name


    def __str__(self):
        return f'{self.user.email} - {self.property.name}'
    

# class PropertyRentingDuration(models.Model):
#     property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='renting_duration')
#     time_in_number = models.IntegerField()
#     currency = models.CharField(max_length=10, choices=Property.CURRENCY, default='Tsh' ) 
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.property.nam



class PropertyRentingDurationOptions(models.Model):
    duration_names = (
        ('night', 'Night'), 
        ('hour', 'Hour'),
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('year', 'Year')
        )   
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='renting_duration_options')
    time_in_number = models.IntegerField()
    time_in_text = models.CharField(max_length=10, choices=duration_names, null = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:




        verbose_name = '12. Renting Duration Options'   
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.property.name
    
