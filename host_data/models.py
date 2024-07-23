from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class PropertyHost(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    property_count = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
    
class PropertyHostVerification(models.Model):
    host = models.ForeignKey(PropertyHost, on_delete=models.CASCADE, related_name='host_verification')
    document = models.FileField(upload_to='host_verification/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.host.user.email
    