"""Forms for searching, filtering, and managing the doctor directory."""

from __future__ import annotations

from django import forms

from apps.accounts.forms import BootstrapFormMixin

from .models import Department, Doctor, DoctorAvailability


class DoctorSearchForm(forms.Form):
    """Powers the search + filter bar on the public doctor directory."""

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search by doctor name or specialty...",
            }
        ),
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        empty_label="All departments",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ("name", "Name (A-Z)"),
            ("-experience_years", "Experience (high to low)"),
            ("consultation_fee", "Fee (low to high)"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class DoctorForm(BootstrapFormMixin, forms.ModelForm):
    """Staff-facing form for creating/updating a doctor profile."""

    class Meta:
        model = Doctor
        fields = [
            "full_name",
            "slug",
            "department",
            "designation",
            "qualifications",
            "experience_years",
            "languages_spoken",
            "consultation_fee",
            "bio",
            "photo",
            "is_active",
            "accepts_walk_ins",
        ]
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}
        help_texts = {"slug": "Used in the doctor's public URL, e.g. 'dr-jane-doe'."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class DoctorAvailabilityForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = DoctorAvailability
        fields = ["weekday", "start_time", "end_time", "slot_minutes"]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class DepartmentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "slug", "description", "icon", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()
