"""Forms for booking and managing appointments."""

from __future__ import annotations

import datetime as dt

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.accounts.forms import BootstrapFormMixin
from apps.doctors.models import Department, Doctor

from .models import Appointment
from .services import get_available_slots


class DoctorSelectWithDepartment(forms.Select):
    """Renders each doctor <option> with a `data-department` attribute so
    app.js can filter the dropdown client-side when the department changes,
    without an extra round-trip to the server."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            doctor = Doctor.objects.filter(pk=value.value if hasattr(value, "value") else value).first()
            if doctor:
                option["attrs"]["data-department"] = str(doctor.department_id)
        return option


class BookAppointmentForm(BootstrapFormMixin, forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    scheduled_time = forms.ChoiceField(
        choices=(), widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Appointment
        fields = ["department", "doctor", "scheduled_date", "scheduled_time", "reason"]
        widgets = {
            "doctor": DoctorSelectWithDepartment,
            "scheduled_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["doctor"].queryset = Doctor.objects.filter(is_active=True)
        self.fields["doctor"].widget.attrs["class"] = "form-select"

        # Populate the time-slot choices from posted/initial data so the
        # form can validate server-side even though the options are also
        # refreshed client-side via the AJAX endpoint (progressive
        # enhancement: works with JS off, just with a manual refresh).
        doctor = None
        target_date = None
        if self.data.get("doctor"):
            doctor = Doctor.objects.filter(pk=self.data.get("doctor")).first()
        if self.data.get("scheduled_date"):
            try:
                target_date = dt.date.fromisoformat(self.data["scheduled_date"])
            except ValueError:
                target_date = None

        if doctor and target_date:
            slots = get_available_slots(doctor, target_date)
            self.fields["scheduled_time"].choices = [
                (slot.strftime("%H:%M"), slot.strftime("%I:%M %p")) for slot in slots
            ]
        else:
            self.fields["scheduled_time"].choices = []

        self._apply_bootstrap()

    def clean_scheduled_date(self):
        target_date = self.cleaned_data["scheduled_date"]
        if target_date < timezone.localdate():
            raise ValidationError("Appointment date cannot be in the past.")
        return target_date

    def clean(self):
        cleaned = super().clean()
        doctor = cleaned.get("doctor")
        department = cleaned.get("department")
        if doctor and department and doctor.department_id != department.id:
            raise ValidationError(
                "The selected doctor does not belong to the selected department."
            )
        return cleaned


class AppointmentStatusForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["status", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class AppointmentFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search patient or doctor..."}
        ),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "All statuses")] + list(Appointment.Status.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    date_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    date_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
