from __future__ import annotations

from django import forms

from apps.accounts.forms import BootstrapFormMixin

from .models import AmbulanceRequest


class AmbulanceRequestForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AmbulanceRequest
        fields = [
            "contact_name",
            "contact_phone",
            "pickup_address",
            "patient_condition",
            "priority",
        ]
        widgets = {
            "pickup_address": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class AmbulanceStatusForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AmbulanceRequest
        fields = ["status", "dispatcher_notes"]
        widgets = {"dispatcher_notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()
