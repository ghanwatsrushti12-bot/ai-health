"""User model and role-based access control primitives for CarePulse."""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class Role(models.TextChoices):
    """Every account belongs to exactly one primary role.

    Fine-grained permissions still flow through Django's standard
    Group/Permission system (see ``apps.accounts.signals``), so admins can
    layer extra permissions on top of a role without a code change.
    """

    PATIENT = "patient", "Patient"
    DOCTOR = "doctor", "Doctor"
    STAFF = "staff", "Front-desk Staff"
    ADMIN = "admin", "Administrator"


phone_validator = RegexValidator(
    regex=r"^\+?[0-9]{7,15}$",
    message="Enter a valid phone number (7-15 digits, optional leading +).",
)


class User(AbstractUser):
    """Extends Django's built-in user with the fields CarePulse needs.

    Keeping this as a thin ``AbstractUser`` subclass (rather than a fully
    custom model) preserves compatibility with ``django.contrib.auth`` and
    third-party packages while still letting us swap in project-specific
    fields from day one, which is the recommended Django best practice.
    """

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.PATIENT,
        help_text="Primary role that determines the user's dashboard and permissions.",
    )
    phone_number = models.CharField(
        max_length=17, blank=True, validators=[phone_validator]
    )
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/%Y/%m/", blank=True, null=True)
    bio = models.CharField(max_length=255, blank=True)
    theme_preference = models.CharField(
        max_length=6,
        choices=[("light", "Light"), ("dark", "Dark")],
        default="light",
    )
    is_verified = models.BooleanField(
        default=False, help_text="Set once contact details are confirmed."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["role"])]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.get_full_name() or self.username

    @property
    def is_patient(self) -> bool:
        return self.role == Role.PATIENT

    @property
    def is_doctor_role(self) -> bool:
        return self.role == Role.DOCTOR

    @property
    def is_staff_role(self) -> bool:
        return self.role in (Role.STAFF, Role.ADMIN)
