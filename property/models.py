from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model



User = get_user_model()


# // category model
class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class PropertyOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    property_count = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
    
     

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




    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  
    price = models.DecimalField(max_digits=10, decimal_places=2, ) 
    currency = models.CharField(max_length=10, choices=CURRENCY, default='Tsh' ) 
    period = models.CharField(max_length=10, choices=period, default='night')
    description = models.TextField()
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)  
    longitude = models.DecimalField(max_digits=9, decimal_places=6)  
    image = models.ImageField(upload_to='property_pics/', null=True, blank=True)  
    owner = models.ForeignKey(PropertyOwner, on_delete=models.CASCADE)
    availability_status = models.BooleanField(default=True, choices=AVAILABILITY_STATUS )
    publication_status = models.BooleanField(default=True, choices=PUBLICATION_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class PropertyImages(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property_pics/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.property.name
    
class PropertyFacility(models.Model):
    property = models.ForeignKey(Property, related_name='facilities', on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    facility = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.facility
    
class PropertyAmenity(models.Model):
    property = models.ForeignKey(Property, related_name='amenities', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class PropertyReview(models.Model):
    property = models.ForeignKey(Property, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField()
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} - {self.property.name}'