# users/models.py
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser,  Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from phone_field import PhoneField
from django.utils.translation import gettext_lazy as _



from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames. The manager class defines
    the create_user and create_superuser methods.
    """
    def create_user(self, email, password=None, date_of_birth=None, phone_number=None, **extra_fields):
        """
        Create and save a regular user with the given email, date of birth, and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, date_of_birth=date_of_birth,phone_number=phone_number **extra_fields)
        user.set_password(password)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, date_of_birth=None, **extra_fields):
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

        return self.create_user(email, password, date_of_birth, **extra_fields)
    

class CustomUser(AbstractUser):
    username = None  # Nullify username
    email = models.EmailField(_("email address"), unique=True)
    date_of_birth = models.DateField(verbose_name="Birthday", null=True)
    phone_number = models.CharField(max_length=15, verbose_name="Phone Number", null=True)

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
    REQUIRED_FIELDS = ["first_name", "last_name", "date_of_birth"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    

class VerificationCode(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='verification_code'  )
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    otp_used = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email