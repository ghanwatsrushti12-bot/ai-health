"""Role-aware analytics dashboard."""

from __future__ import annotations

import datetime as dt
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import TemplateView

from apps.ambulance.models import AmbulanceRequest
from apps.appointments.models import Appointment
from apps.doctors.models import Department, Doctor
from apps.feedback.models import Feedback
from apps.triage.models import TriageAssessment

from .models import Notification


class DashboardView(LoginRequiredMixin, TemplateView):
    """Single entry point at /dashboard/ that renders a different layout
    depending on the logged-in user's role, while sharing one URL and one
    navigation shell."""

    def get_template_names(self):
        user = self.request.user
        if user.is_staff_role or user.is_superuser:
            return ["dashboard/admin_dashboard.html"]
        if user.is_doctor_role:
            return ["dashboard/doctor_dashboard.html"]
        return ["dashboard/patient_dashboard.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.localdate()

        if user.is_staff_role or user.is_superuser:
            context.update(self._admin_context(today))
        elif user.is_doctor_role and hasattr(user, "doctor_profile"):
            context.update(self._doctor_context(user.doctor_profile, today))
        else:
            context.update(self._patient_context(user, today))
        return context

    # -- role-specific context builders --------------------------------
    def _admin_context(self, today):
        appointments = Appointment.objects.all()
        status_counts = dict(
            appointments.values_list("status").annotate(count=Count("id"))
        )
        last_7_days = [today - dt.timedelta(days=i) for i in range(6, -1, -1)]
        daily_counts = [
            appointments.filter(scheduled_date=day).count() for day in last_7_days
        ]
        by_department = list(
            appointments.values("department__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:6]
        )

        return {
            "total_appointments": appointments.count(),
            "today_appointments": appointments.filter(scheduled_date=today).count(),
            "pending_appointments": status_counts.get("pending", 0),
            "total_doctors": Doctor.objects.filter(is_active=True).count(),
            "total_departments": Department.objects.filter(is_active=True).count(),
            "active_ambulance_requests": AmbulanceRequest.objects.exclude(
                status__in=[
                    AmbulanceRequest.Status.COMPLETED,
                    AmbulanceRequest.Status.CANCELLED,
                ]
            ).count(),
            "average_rating": round(
                Feedback.objects.aggregate(avg=Avg("rating"))["avg"] or 0, 2
            ),
            "chart_labels": json.dumps([d.strftime("%b %d") for d in last_7_days]),
            "chart_daily_counts": json.dumps(daily_counts),
            "chart_status_labels": json.dumps(
                [Appointment.Status(s).label for s in status_counts.keys()]
            ),
            "chart_status_counts": json.dumps(list(status_counts.values())),
            "chart_department_labels": json.dumps(
                [row["department__name"] for row in by_department]
            ),
            "chart_department_counts": json.dumps(
                [row["count"] for row in by_department]
            ),
            "recent_appointments": appointments.select_related(
                "patient", "doctor", "department"
            ).order_by("-created_at")[:6],
        }

    def _doctor_context(self, doctor, today):
        appointments = Appointment.objects.filter(doctor=doctor)
        return {
            "doctor": doctor,
            "today_appointments": appointments.filter(
                scheduled_date=today
            ).order_by("scheduled_time"),
            "upcoming_count": appointments.filter(scheduled_date__gte=today).count(),
            "completed_count": appointments.filter(
                status=Appointment.Status.COMPLETED
            ).count(),
            "total_patients": appointments.values("patient").distinct().count(),
        }

    def _patient_context(self, user, today):
        appointments = Appointment.objects.filter(patient=user)
        return {
            "upcoming_appointments": appointments.filter(
                scheduled_date__gte=today
            ).order_by("scheduled_date", "scheduled_time")[:5],
            "appointment_count": appointments.count(),
            "triage_count": TriageAssessment.objects.filter(patient=user).count(),
            "ambulance_count": AmbulanceRequest.objects.filter(requester=user).count(),
            "recent_triage": TriageAssessment.objects.filter(patient=user)
            .select_related("predicted_condition")
            .order_by("-created_at")[:3],
        }


class MarkNotificationReadView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        notification = get_object_or_404(
            Notification, pk=kwargs["pk"], recipient=request.user
        )
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return redirect(notification.link or "dashboard:home")
