"""Public doctor directory + staff-only management views."""

from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.core.mixins import StaffOrAdminRequiredMixin

from .forms import DoctorAvailabilityForm, DoctorForm, DoctorSearchForm
from .models import Department, Doctor, DoctorAvailability

logger = logging.getLogger("carepulse")


class DepartmentListView(ListView):
    model = Department
    template_name = "doctors/department_list.html"
    context_object_name = "departments"

    def get_queryset(self):
        return Department.objects.filter(is_active=True).order_by("name")


class DepartmentDetailView(DetailView):
    model = Department
    template_name = "doctors/department_detail.html"
    context_object_name = "department"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctors"] = self.object.doctors.filter(is_active=True)
        return context


class DoctorListView(ListView):
    """Searchable, filterable, paginated public doctor directory."""

    model = Doctor
    template_name = "doctors/doctor_list.html"
    context_object_name = "doctors"
    paginate_by = 9

    def get_queryset(self):
        queryset = Doctor.objects.select_related("department").filter(is_active=True)
        self.form = DoctorSearchForm(self.request.GET or None)
        if self.form.is_valid():
            query = self.form.cleaned_data.get("q")
            department = self.form.cleaned_data.get("department")
            sort = self.form.cleaned_data.get("sort")
            if query:
                queryset = queryset.filter(
                    Q(full_name__icontains=query)
                    | Q(designation__icontains=query)
                    | Q(department__name__icontains=query)
                )
            if department:
                queryset = queryset.filter(department=department)
            if sort == "name":
                queryset = queryset.order_by("full_name")
            elif sort:
                queryset = queryset.order_by(sort)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        context["departments"] = Department.objects.filter(is_active=True)
        return context


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = "doctors/doctor_detail.html"
    context_object_name = "doctor"

    def get_queryset(self):
        return Doctor.objects.select_related("department").prefetch_related(
            "availability_slots"
        )


# ---------------------------------------------------------------------------
# Staff-only management (create/update/delete doctors & availability)
# ---------------------------------------------------------------------------
class DoctorCreateView(LoginRequiredMixin, StaffOrAdminRequiredMixin, CreateView):
    model = Doctor
    form_class = DoctorForm
    template_name = "doctors/doctor_form.html"
    success_url = reverse_lazy("doctors:manage_list")

    def form_valid(self, form):
        if not form.cleaned_data.get("slug"):
            form.instance.slug = slugify(form.cleaned_data["full_name"])
        messages.success(self.request, "Doctor profile created.")
        logger.info("Doctor created by %s", self.request.user)
        return super().form_valid(form)


class DoctorUpdateView(LoginRequiredMixin, StaffOrAdminRequiredMixin, UpdateView):
    model = Doctor
    form_class = DoctorForm
    template_name = "doctors/doctor_form.html"
    success_url = reverse_lazy("doctors:manage_list")

    def form_valid(self, form):
        messages.success(self.request, "Doctor profile updated.")
        return super().form_valid(form)


class DoctorDeleteView(LoginRequiredMixin, StaffOrAdminRequiredMixin, DeleteView):
    model = Doctor
    template_name = "doctors/doctor_confirm_delete.html"
    success_url = reverse_lazy("doctors:manage_list")

    def form_valid(self, form):
        messages.success(self.request, "Doctor profile removed.")
        logger.warning("Doctor %s deleted by %s", self.object, self.request.user)
        return super().form_valid(form)


class DoctorManageListView(LoginRequiredMixin, StaffOrAdminRequiredMixin, ListView):
    """Staff dashboard view listing every doctor (active + inactive)."""

    model = Doctor
    template_name = "doctors/doctor_manage_list.html"
    context_object_name = "doctors"
    paginate_by = 12

    def get_queryset(self):
        queryset = Doctor.objects.select_related("department").order_by("full_name")
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(full_name__icontains=query)
        return queryset


class DoctorAvailabilityCreateView(
    LoginRequiredMixin, StaffOrAdminRequiredMixin, CreateView
):
    model = DoctorAvailability
    form_class = DoctorAvailabilityForm
    template_name = "doctors/availability_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.doctor = get_object_or_404(Doctor, pk=kwargs["doctor_id"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.doctor = self.doctor
        messages.success(self.request, "Availability slot added.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctor"] = self.doctor
        return context

    def get_success_url(self):
        return reverse_lazy("doctors:manage_detail", kwargs={"pk": self.doctor.pk})


class DoctorManageDetailView(LoginRequiredMixin, StaffOrAdminRequiredMixin, DetailView):
    model = Doctor
    template_name = "doctors/doctor_manage_detail.html"
    context_object_name = "doctor"


def delete_availability_slot(request, pk):
    slot = get_object_or_404(DoctorAvailability, pk=pk)
    doctor_pk = slot.doctor_id
    if request.method == "POST" and request.user.is_authenticated and (
        request.user.is_staff_role or request.user.is_superuser
    ):
        slot.delete()
        messages.success(request, "Availability slot removed.")
    return redirect("doctors:manage_detail", pk=doctor_pk)
