from django.contrib import admin

# Register your models here.
# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, VerificationCode  


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    list_display = (
        "email",
        "first_name",
        "last_name",
        "date_of_birth",
        "phone_number", 
        "is_staff",
        "is_active",
        "last_login",
    )
    list_filter = (
        "email",
        "first_name",
        "last_name",
        "date_of_birth",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": (
            "first_name",
            "last_name", 
            "email", 
            "password", 
            "date_of_birth")}
        ),
        ("Permissions", {"fields": (
            "is_staff", 
            "is_active", 
            "groups", 
            "user_permissions")}
        ),
    )
    add_fieldsets = (
        ( None, {"fields": (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password1",
            "password2",
            "date_of_birth",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions")}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at", "updated_at")
    search_fields = ("user", "code")
    ordering = ("created_at",)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(VerificationCode, VerificationCodeAdmin)


    