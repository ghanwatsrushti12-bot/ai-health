"""Symptom-checker domain models.

Design note: the original prototype trained an opaque TF-IDF + Naive
Bayes classifier against a static CSV and pickled it to disk. This
schema instead stores symptoms and conditions as first-class, admin
editable rows with an explicit many-to-many relationship, so:

* the mapping is transparent and auditable (a clinician can review it
  in the admin panel),
* it can be updated without retraining anything, and
* the scoring in ``apps.triage.services`` is a simple, explainable
  overlap score rather than a black box.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.doctors.models import Department


class Symptom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Condition(models.Model):
    class Severity(models.TextChoices):
        LOW = "low", "Low - self-care likely sufficient"
        MODERATE = "moderate", "Moderate - consult a doctor soon"
        HIGH = "high", "High - seek care promptly"
        EMERGENCY = "emergency", "Emergency - seek immediate care"

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    severity = models.CharField(
        max_length=10, choices=Severity.choices, default=Severity.MODERATE
    )
    symptoms = models.ManyToManyField(Symptom, related_name="conditions")
    recommended_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recommended_for_conditions",
    )
    self_care_advice = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class TriageAssessment(models.Model):
    """A record of one symptom-check session for audit / history."""

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="triage_assessments",
        null=True,
        blank=True,
    )
    reported_symptoms = models.ManyToManyField(Symptom, related_name="assessments")
    predicted_condition = models.ForeignKey(
        Condition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assessments",
    )
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Assessment #{self.pk} - {self.predicted_condition or 'Unclear'}"
