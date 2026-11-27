from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CarePulseUserAdmin(UserAdmin):
    """Extends Django's default UserAdmin with CarePulse-specific fields."""

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_verified",
        "is_active",
        "created_at",
    )
    list_filter = ("role", "is_active", "is_verified", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")
    ordering = ("-created_at",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "CarePulse profile",
            {
                "fields": (
                    "role",
                    "phone_number",
                    "date_of_birth",
                    "avatar",
                    "bio",
                    "theme_preference",
                    "is_verified",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("CarePulse profile", {"fields": ("role", "email", "phone_number")}),
    )
