"""Views for booking, listing, and managing appointments."""

from __future__ import annotations

import datetime as dt
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from apps.core.mixins import StaffOrAdminRequiredMixin
from apps.doctors.models import Doctor

from .forms import AppointmentFilterForm, AppointmentStatusForm, BookAppointmentForm
from .models import Appointment
from .services import get_available_slots

logger = logging.getLogger("carepulse")


class BookAppointmentView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = BookAppointmentForm
    template_name = "appointments/book.html"
    success_url = reverse_lazy("appointments:list")

    def get_initial(self):
        initial = super().get_initial()
        doctor_id = self.request.GET.get("doctor")
        if doctor_id:
            doctor = Doctor.objects.filter(pk=doctor_id).first()
            if doctor:
                initial["doctor"] = doctor.pk
                initial["department"] = doctor.department_id
        return initial

    def form_valid(self, form):
        form.instance.patient = self.request.user
        form.instance.scheduled_time = dt.time.fromisoformat(
            form.cleaned_data["scheduled_time"]
        )
        response = super().form_valid(form)
        logger.info(
            "Appointment booked: patient=%s doctor=%s date=%s",
            self.request.user,
            form.instance.doctor,
            form.instance.scheduled_date,
        )
        messages.success(
            self.request,
            "Your appointment request has been submitted. "
            "You will see it under 'My Appointments'.",
        )
        return response


class AvailableSlotsView(LoginRequiredMixin, View):
    """AJAX endpoint: returns open time slots for a doctor + date."""

    def get(self, request, *args, **kwargs):
        doctor_id = request.GET.get("doctor")
        date_str = request.GET.get("date")
        try:
            doctor = Doctor.objects.get(pk=doctor_id)
            target_date = dt.date.fromisoformat(date_str)
        except (Doctor.DoesNotExist, TypeError, ValueError):
            return JsonResponse({"slots": []})

        slots = get_available_slots(doctor, target_date)
        return JsonResponse(
            {
                "slots": [
                    {"value": s.strftime("%H:%M"), "label": s.strftime("%I:%M %p")}
                    for s in slots
                ]
            }
        )


class AppointmentListView(LoginRequiredMixin, ListView):
    """Role-aware list: patients see their own; staff/doctors see everyone's."""

    model = Appointment
    template_name = "appointments/list.html"
    context_object_name = "appointments"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related(
            "doctor", "department", "patient"
        )
        if user.is_staff_role or user.is_superuser:
            pass  # staff/admin can see every appointment
        elif user.is_doctor_role and hasattr(user, "doctor_profile"):
            queryset = queryset.filter(doctor=user.doctor_profile)
        else:
            queryset = queryset.filter(patient=user)

        self.form = AppointmentFilterForm(self.request.GET or None)
        if self.form.is_valid():
            data = self.form.cleaned_data
            if data.get("q"):
                from django.db.models import Q

                queryset = queryset.filter(
                    Q(patient__first_name__icontains=data["q"])
                    | Q(patient__last_name__icontains=data["q"])
                    | Q(doctor__full_name__icontains=data["q"])
                )
            if data.get("status"):
                queryset = queryset.filter(status=data["status"])
            if data.get("date_from"):
                queryset = queryset.filter(scheduled_date__gte=data["date_from"])
            if data.get("date_to"):
                queryset = queryset.filter(scheduled_date__lte=data["date_to"])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        return context


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    model = Appointment
    template_name = "appointments/detail.html"
    context_object_name = "appointment"

    def get_queryset(self):
        return Appointment.objects.select_related("doctor", "department", "patient")


class CancelAppointmentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        appointment = Appointment.objects.filter(pk=pk).first()
        if not appointment:
            messages.error(request, "Appointment not found.")
            return self._redirect()

        can_cancel = (
            appointment.patient_id == request.user.id
            or request.user.is_staff_role
            or request.user.is_superuser
        )
        if not can_cancel:
            messages.error(request, "You cannot cancel this appointment.")
            return self._redirect()

        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=["status", "updated_at"])
        messages.success(request, "Appointment cancelled.")
        return self._redirect()

    def _redirect(self):
        from django.shortcuts import redirect

        return redirect("appointments:list")


class AppointmentStatusUpdateView(
    LoginRequiredMixin, StaffOrAdminRequiredMixin, UpdateView
):
    """Lets staff/doctors move an appointment through its lifecycle."""

    model = Appointment
    form_class = AppointmentStatusForm
    template_name = "appointments/status_form.html"

    def get_success_url(self):
        return reverse_lazy("appointments:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Appointment status updated.")
        return super().form_valid(form)
