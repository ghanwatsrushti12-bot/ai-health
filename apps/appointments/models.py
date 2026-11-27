"""Appointment scheduling model.

A database-level uniqueness constraint on (doctor, date, time) is the
source of truth that prevents double-booking — the same guarantee the
original prototype only attempted at the application layer.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.urls import reverse

from apps.doctors.models import Department, Doctor


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending confirmation"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No-show"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="appointments"
    )
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="appointments"
    )
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    reason = models.CharField(
        max_length=255, help_text="Brief reason for the visit, e.g. 'Follow-up'."
    )
    notes = models.TextField(blank=True, help_text="Internal notes added by staff.")
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_date", "-scheduled_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "scheduled_date", "scheduled_time"],
                condition=~models.Q(status="cancelled"),
                name="unique_active_doctor_slot",
            )
        ]
        indexes = [
            models.Index(fields=["scheduled_date", "status"]),
            models.Index(fields=["patient", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.patient} with Dr. {self.doctor.full_name} on {self.scheduled_date} {self.scheduled_time}"

    def get_absolute_url(self):
        return reverse("appointments:detail", kwargs={"pk": self.pk})

    @property
    def is_upcoming(self) -> bool:
        from django.utils import timezone

        return self.scheduled_date >= timezone.localdate() and self.status in (
            self.Status.PENDING,
            self.Status.CONFIRMED,
        )

    @property
    def status_badge_class(self) -> str:
        return {
            self.Status.PENDING: "bg-warning-subtle text-warning-emphasis",
            self.Status.CONFIRMED: "bg-info-subtle text-info-emphasis",
            self.Status.COMPLETED: "bg-success-subtle text-success-emphasis",
            self.Status.CANCELLED: "bg-danger-subtle text-danger-emphasis",
            self.Status.NO_SHOW: "bg-secondary-subtle text-secondary-emphasis",
        }.get(self.status, "bg-secondary-subtle")
