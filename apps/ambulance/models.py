"""Ambulance dispatch request model."""

from __future__ import annotations

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r"^\+?[0-9]{7,15}$",
    message="Enter a valid phone number.",
)


class AmbulanceRequest(models.Model):
    class Priority(models.TextChoices):
        CRITICAL = "critical", "Critical - life threatening"
        URGENT = "urgent", "Urgent"
        STANDARD = "standard", "Standard transport"

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        DISPATCHED = "dispatched", "Ambulance dispatched"
        ARRIVED = "arrived", "Arrived at location"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ambulance_requests",
    )
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=17, validators=[phone_validator])
    pickup_address = models.TextField()
    patient_condition = models.CharField(
        max_length=255, help_text="Brief description, e.g. 'Chest pain, conscious'."
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.STANDARD
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.REQUESTED
    )
    dispatcher_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "priority"])]

    def __str__(self) -> str:
        return f"{self.contact_name} - {self.get_priority_display()} ({self.status})"

    @property
    def priority_badge_class(self) -> str:
        return {
            self.Priority.CRITICAL: "bg-danger",
            self.Priority.URGENT: "bg-warning text-dark",
            self.Priority.STANDARD: "bg-secondary",
        }.get(self.priority, "bg-secondary")
