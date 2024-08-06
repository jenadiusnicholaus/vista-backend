# users/models.py
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser,  Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from phone_field import PhoneField
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError



from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames. The manager class defines
    the create_user and create_superuser methods.
    """
    def create_user(self, email, password=None, date_of_birth=None, phone_number=None, agreed_to_Terms=None, **extra_fields):
        """
        Create and save a regular user with the given email, date of birth, and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, date_of_birth=date_of_birth, phone_number=phone_number, agreed_to_Terms=agreed_to_Terms, **extra_fields)
        user.set_password(password)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_active', False) 
        extra_fields.setdefault('is_superuser', False)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, date_of_birth=None, phone_number=None,agreed_to_Terms=None, **extra_fields):
        """
        Create and save a superuser with the given email, date of birth, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, date_of_birth, phone_number, agreed_to_Terms,  **extra_fields)
    

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    date_of_birth = models.DateField(verbose_name="Birthday", null=True)
    phone_number = models.CharField(max_length=15, verbose_name="Phone Number", null=True)
    agreed_to_Terms = models.BooleanField(default=False)
    user_profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True) 


    # Override groups and user_permissions fields to add related_name
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="customuser_set",  # Changed related_name
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="customuser_set",  # Changed related_name
        related_query_name="customuser",
    )
    last_login = models.DateTimeField(_("last login"), auto_now=False, null=True, blank=True    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "date_of_birth", "phone_number", "agreed_to_Terms"]
    phone_is_verified = models.BooleanField(default=False)
    

    objects = CustomUserManager()
    class Meta:
        unique_together = ('email', 'phone_number')

 

    def __str__(self):
        if self.email is not None:
            return self.email
        return self.phone_number    
    

class VerificationCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verification_code'  )
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    otp_used = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email
    

class AzamPayAuthToken(models.Model):
    access_token = models.TextField(null=True, blank=True)
    refresh_token = models.TextField( null=True, blank=True)
    token_type = models.CharField(max_length=255, default='Bearer', null=True, blank=True)
    expires_in = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Device(models.Model):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fcm_devices', null=True, blank=True)
    device_id = models.CharField(max_length=255, unique=True)
    registration_id = models.CharField(max_length=255)
    # device fcm registration token
    # device_fcmrtoken = models.CharField(max_length=255)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    device_name = models.CharField(max_length=255)
    device = models.CharField(max_length=255)
    device_type = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_physical_device = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.device_name

  