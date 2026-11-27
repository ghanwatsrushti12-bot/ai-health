from django.contrib import admin

from .models import AmbulanceRequest


@admin.register(AmbulanceRequest)
class AmbulanceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "contact_name",
        "contact_phone",
        "priority",
        "status",
        "created_at",
    )
    list_filter = ("priority", "status")
    search_fields = ("contact_name", "contact_phone", "pickup_address")
    date_hierarchy = "created_at"
