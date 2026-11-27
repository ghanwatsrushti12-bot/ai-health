"""Public marketing pages + custom error handlers."""

from __future__ import annotations

from django.shortcuts import render
from django.views.generic import TemplateView

from apps.doctors.models import Department, Doctor
from apps.feedback.models import Feedback


class LandingPageView(TemplateView):
    template_name = "core/landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["departments"] = Department.objects.filter(is_active=True)[:6]
        context["doctors"] = Doctor.objects.filter(is_active=True).select_related(
            "department"
        )[:4]
        context["testimonials"] = Feedback.objects.filter(
            is_published=True
        ).select_related("author")[:3]
        return context


class AboutView(TemplateView):
    template_name = "core/about.html"


class ContactView(TemplateView):
    template_name = "core/contact.html"


# ---------------------------------------------------------------------------
# Custom error handlers (wired up in carepulse/urls.py)
# ---------------------------------------------------------------------------
def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    return render(request, "errors/500.html", status=500)


def error_403(request, exception=None):
    return render(request, "errors/403.html", status=403)


def error_400(request, exception=None):
    return render(request, "errors/400.html", status=400)
