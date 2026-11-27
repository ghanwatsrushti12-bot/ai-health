"""Symptom-selection form for the triage tool."""

from __future__ import annotations

from django import forms

from .models import Symptom


class SymptomCheckerForm(forms.Form):
    symptoms = forms.ModelMultipleChoiceField(
        queryset=Symptom.objects.all().order_by("name"),
        widget=forms.CheckboxSelectMultiple,
        label="Select all symptoms you are experiencing",
    )

    def clean_symptoms(self):
        symptoms = self.cleaned_data["symptoms"]
        if not symptoms:
            raise forms.ValidationError("Please select at least one symptom.")
        return symptoms
