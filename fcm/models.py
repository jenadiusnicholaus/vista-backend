from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from vasta_settings import settings   

User = get_user_model()
from django.db import models
from django.utils import timezone
import datetime
import pytz


class FcmTokenModel(models.Model):
    STALE_TIME = (
        ('1m', '1 Minute'),
        ('5m', '5 Minutes'),
        ('10m', '10 Minutes'),
        ('1', '1 Day'),
        ('3', '3 Days'),
        ('7', '1 Week'),
        ('14', '2 Weeks'),
        ('30', '1 Month'),
        ('90', '3 Months'),
        ('180', '6 Months'),
        ('365', '1 Year'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fcm_tokens', null=True, blank=True)
    fcm_token = models.CharField(max_length=1000)
    time_stamp = models.DateTimeField(auto_now_add=True)
    is_stale = models.BooleanField(default=False)
    stale_time = models.CharField(max_length=255, choices=STALE_TIME, default='1')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        verbose_name = 'FCM Token'
        verbose_name_plural = 'FCM Tokens'

    def __str__(self):
        return self.fcm_token
    
    def save(self, *args, **kwargs):
        self.is_stale = self.isStale()
        super(FcmTokenModel, self).save(*args, **kwargs)



    def isStale(self):
        try:
            # Ensure time_stamp is not None
            if self.time_stamp is None:
                print("Error: time_stamp is None")
                return False

            # Define the local timezone
            local_tz = pytz.timezone('Africa/Dar_es_Salaam')

            if self.stale_time.endswith('m'):
                minutes = int(self.stale_time[:-1])
                expiration_time = self.time_stamp + datetime.timedelta(minutes=minutes)
            else:
                days = int(self.stale_time)
                expiration_time = self.time_stamp + datetime.timedelta(days=days)
            
            # Ensure both timestamps are timezone-aware and converted to local timezone
            if timezone.is_naive(expiration_time):
                expiration_time = timezone.make_aware(expiration_time, timezone.get_current_timezone())
            expiration_time = expiration_time.astimezone(local_tz)
            
            current_time = timezone.now().astimezone(local_tz)

            print(f"Expiration Time: {expiration_time}")
            print(f"Current Time: {current_time}")

            return expiration_time < current_time
        except Exception as e:
            print(f"Error in isStale: {e}")
            return False

            
class FcmNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fcm_notifications', null=True, blank=True)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fcm_notifications_to_user', null=True, blank=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title




    
    