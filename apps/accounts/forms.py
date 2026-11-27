"""Forms for registration, profile editing, and preferences."""

from __future__ import annotations

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Role, User


class BootstrapFormMixin:
    """Adds Bootstrap 5 form-control classes to every field automatically.

    Centralising this avoids repeating ``widget=forms.TextInput(attrs=...)``
    boilerplate across every form in the project.
    """

    def _apply_bootstrap(self):
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            if isinstance(field.widget, (forms.CheckboxInput,)):
                field.widget.attrs["class"] = f"{existing} form-check-input".strip()
            else:
                field.widget.attrs["class"] = f"{existing} form-control".strip()
            field.widget.attrs.setdefault("placeholder", field.label)


class PatientSignUpForm(BootstrapFormMixin, UserCreationForm):
    """Public registration form. Always creates a Patient account.

    Staff/Doctor accounts are provisioned by an administrator via the
    admin panel or the staff-management screen — self-service signup for
    elevated roles would be a privilege-escalation hole.
    """

    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=17, required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = Role.PATIENT
        if commit:
            user.save()
        return user


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    """Lets any logged-in user update their own personal details."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "bio",
            "avatar",
        ]
        widgets = {"date_of_birth": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class ThemePreferenceForm(BootstrapFormMixin, forms.ModelForm):
    """Persists the user's light/dark preference server-side.

    The toggle in the navbar flips the theme instantly via JavaScript and
    ``localStorage``; this form is what syncs that choice back to the
    account so it follows the user across devices.
    """

    class Meta:
        model = User
        fields = ["theme_preference"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()
