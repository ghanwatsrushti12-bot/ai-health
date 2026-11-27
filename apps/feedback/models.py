"""Patient feedback / satisfaction survey model."""

from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.doctors.models import Doctor


class Feedback(models.Model):
    class Category(models.TextChoices):
        APPOINTMENT = "appointment", "Appointment experience"
        DOCTOR = "doctor", "Doctor / consultation"
        AMBULANCE = "ambulance", "Ambulance service"
        FACILITY = "facility", "Facility / hospitality"
        OTHER = "other", "Other"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feedback_entries",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feedback_entries",
    )
    category = models.CharField(
        max_length=15, choices=Category.choices, default=Category.OTHER
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1 (poor) to 5 (excellent).",
    )
    message = models.TextField()
    is_published = models.BooleanField(
        default=False, help_text="Show this feedback as a public testimonial."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["category", "rating"])]

    def __str__(self) -> str:
        return f"{self.get_category_display()} - {self.rating}/5"
