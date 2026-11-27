from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "patient",
        "doctor",
        "department",
        "scheduled_date",
        "scheduled_time",
        "status",
    )
    list_filter = ("status", "department", "scheduled_date")
    search_fields = (
        "patient__username",
        "patient__first_name",
        "patient__last_name",
        "doctor__full_name",
    )
    autocomplete_fields = ["doctor", "department"]
    date_hierarchy = "scheduled_date"
    list_select_related = ("patient", "doctor", "department")
