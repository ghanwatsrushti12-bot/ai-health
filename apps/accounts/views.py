"""Views for registration, profile management, and account settings."""

from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from .forms import PatientSignUpForm, ProfileForm, ThemePreferenceForm
from .models import User

logger = logging.getLogger("carepulse")


class SignUpView(CreateView):
    """Public self-service registration; always provisions a Patient role."""

    model = User
    form_class = PatientSignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info("New patient account created: %s", self.object.username)
        messages.success(
            self.request,
            "Account created successfully. You can now sign in.",
        )
        return response


class ProfileView(LoginRequiredMixin, UpdateView):
    """Lets the logged-in user view and edit their own profile."""

    model = User
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated.")
        return super().form_valid(form)


class AccountSettingsView(LoginRequiredMixin, TemplateView):
    """A single settings screen combining theme preference and quick links.

    Password changes are handled by Django's battle-tested
    ``PasswordChangeView`` (wired up separately in urls.py) rather than
    reinvented here, per the Django best-practice of not rolling your own
    password-handling logic.
    """

    template_name = "accounts/settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["theme_form"] = ThemePreferenceForm(instance=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        form = ThemePreferenceForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Preferences saved.")
        else:
            messages.error(request, "Could not save preferences.")
        return self.get(request, *args, **kwargs)


class CarePulsePasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:settings")

    def form_valid(self, form):
        messages.success(self.request, "Password updated successfully.")
        return super().form_valid(form)
