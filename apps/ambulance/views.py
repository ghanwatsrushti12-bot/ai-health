"""Views for requesting and dispatching ambulances."""

from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.core.mixins import StaffOrAdminRequiredMixin

from .forms import AmbulanceRequestForm, AmbulanceStatusForm
from .models import AmbulanceRequest

logger = logging.getLogger("carepulse")


class AmbulanceRequestCreateView(CreateView):
    """Anyone can request an ambulance — including anonymous visitors in
    an emergency — so this view is intentionally not login-gated."""

    model = AmbulanceRequest
    form_class = AmbulanceRequestForm
    template_name = "ambulance/request_form.html"
    success_url = reverse_lazy("ambulance:request_success")

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.requester = self.request.user
        response = super().form_valid(form)
        logger.warning(
            "Ambulance requested: %s priority=%s",
            form.instance.contact_name,
            form.instance.priority,
        )
        messages.success(
            self.request,
            "Ambulance request received. Our dispatch team has been notified.",
        )
        return response


class AmbulanceRequestSuccessView(DetailView):
    template_name = "ambulance/request_success.html"

    def get(self, request, *args, **kwargs):
        from django.shortcuts import render

        return render(request, self.template_name)


class AmbulanceRequestListView(
    LoginRequiredMixin, StaffOrAdminRequiredMixin, ListView
):
    model = AmbulanceRequest
    template_name = "ambulance/request_list.html"
    context_object_name = "requests"
    paginate_by = 10

    def get_queryset(self):
        queryset = AmbulanceRequest.objects.all()
        status = self.request.GET.get("status")
        priority = self.request.GET.get("priority")
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = AmbulanceRequest.Status.choices
        context["priority_choices"] = AmbulanceRequest.Priority.choices
        return context


class AmbulanceRequestUpdateView(
    LoginRequiredMixin, StaffOrAdminRequiredMixin, UpdateView
):
    model = AmbulanceRequest
    form_class = AmbulanceStatusForm
    template_name = "ambulance/status_form.html"
    success_url = reverse_lazy("ambulance:request_list")

    def form_valid(self, form):
        messages.success(self.request, "Ambulance request updated.")
        return super().form_valid(form)
