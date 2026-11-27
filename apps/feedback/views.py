"""Views for submitting and reviewing patient feedback."""

from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from apps.core.mixins import StaffOrAdminRequiredMixin

from .forms import FeedbackForm
from .models import Feedback

logger = logging.getLogger("carepulse")


class FeedbackCreateView(LoginRequiredMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = "feedback/submit.html"
    success_url = reverse_lazy("feedback:thanks")

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Thank you for your feedback!")
        return response


class FeedbackThanksView(ListView):
    """Renders a short thank-you screen (kept as a template-only view)."""

    template_name = "feedback/thanks.html"
    model = Feedback

    def get_queryset(self):
        return Feedback.objects.none()


class FeedbackManageListView(LoginRequiredMixin, StaffOrAdminRequiredMixin, ListView):
    model = Feedback
    template_name = "feedback/manage_list.html"
    context_object_name = "feedback_entries"
    paginate_by = 10

    def get_queryset(self):
        queryset = Feedback.objects.select_related("author", "doctor")
        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = Feedback.objects.aggregate(average=Avg("rating"), total=Count("id"))
        context["average_rating"] = round(stats["average"] or 0, 2)
        context["total_feedback"] = stats["total"]
        context["category_choices"] = Feedback.Category.choices
        return context
