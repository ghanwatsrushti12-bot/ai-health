from django.contrib import admin

from .models import Condition, Symptom, TriageAssessment


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ("name", "severity", "recommended_department")
    list_filter = ("severity", "recommended_department")
    search_fields = ("name",)
    filter_horizontal = ("symptoms",)
    autocomplete_fields = ["recommended_department"]


@admin.register(TriageAssessment)
class TriageAssessmentAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "predicted_condition", "confidence_score", "created_at")
    list_filter = ("predicted_condition",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
