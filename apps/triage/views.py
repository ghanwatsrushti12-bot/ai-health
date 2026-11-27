"""Views for the symptom-checker (triage) tool."""

from __future__ import annotations

import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, ListView

from .forms import SymptomCheckerForm
from .models import TriageAssessment
from .services import assess_symptoms

logger = logging.getLogger("carepulse")


class SymptomCheckerView(FormView):
    """Public-facing symptom checker. Works for anonymous visitors too,
    but saves a history record only when the user is authenticated."""

    form_class = SymptomCheckerForm
    template_name = "triage/checker.html"

    def form_valid(self, form):
        symptoms = form.cleaned_data["symptoms"]
        result = assess_symptoms([s.pk for s in symptoms])

        assessment = None
        if self.request.user.is_authenticated:
            assessment = TriageAssessment.objects.create(
                patient=self.request.user,
                predicted_condition=result.condition,
                confidence_score=result.confidence,
            )
            assessment.reported_symptoms.set(symptoms)
            logger.info(
                "Triage assessment #%s for %s -> %s (%.1f%%)",
                assessment.pk,
                self.request.user,
                result.condition,
                result.confidence,
            )

        return self.render_to_response(
            self.get_context_data(form=form, result=result, submitted=True)
        )


class TriageHistoryListView(LoginRequiredMixin, ListView):
    model = TriageAssessment
    template_name = "triage/history.html"
    context_object_name = "assessments"
    paginate_by = 10

    def get_queryset(self):
        return (
            TriageAssessment.objects.filter(patient=self.request.user)
            .select_related("predicted_condition")
            .prefetch_related("reported_symptoms")
        )
