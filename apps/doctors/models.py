"""Department and doctor directory models.

Compared to a flat "doctor with a free-text availability string" design,
this schema normalises weekly availability into its own table so the
appointments app can compute real open slots instead of parsing text.
"""

from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=50,
        default="bi-heart-pulse",
        help_text="Bootstrap Icons class, e.g. 'bi-heart-pulse'.",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["slug"])]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("doctors:department_detail", kwargs={"slug": self.slug})

    @property
    def doctor_count(self) -> int:
        return self.doctors.filter(is_active=True).count()


class Doctor(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doctor_profile",
        help_text="Optional linked login account for this doctor.",
    )
    full_name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="doctors"
    )
    designation = models.CharField(
        max_length=150, help_text="e.g. 'Senior Consultant Pediatrician'"
    )
    qualifications = models.CharField(max_length=255, help_text="e.g. 'MBBS, MD'")
    experience_years = models.PositiveSmallIntegerField(default=0)
    languages_spoken = models.CharField(
        max_length=255, default="English", help_text="Comma-separated list."
    )
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="doctors/%Y/%m/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    accepts_walk_ins = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["department", "is_active"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return f"Dr. {self.full_name} ({self.department.name})"

    def get_absolute_url(self):
        return reverse("doctors:doctor_detail", kwargs={"slug": self.slug})

    @property
    def language_list(self) -> list[str]:
        return [lang.strip() for lang in self.languages_spoken.split(",") if lang.strip()]


class DoctorAvailability(models.Model):
    """A recurring weekly slot during which a doctor takes appointments."""

    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="availability_slots"
    )
    weekday = models.IntegerField(choices=Doctor.Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_minutes = models.PositiveSmallIntegerField(
        default=20,
        validators=[MinValueValidator(5), MaxValueValidator(120)],
        help_text="Length of a single bookable appointment slot, in minutes.",
    )

    class Meta:
        ordering = ["weekday", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "weekday", "start_time", "end_time"],
                name="unique_doctor_weekday_slot",
            ),
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F("start_time")),
                name="availability_end_after_start",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.doctor} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"
