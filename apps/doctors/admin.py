from django.contrib import admin

from .models import Department, Doctor, DoctorAvailability


class DoctorAvailabilityInline(admin.TabularInline):
    model = DoctorAvailability
    extra = 1


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "doctor_count", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "department",
        "designation",
        "experience_years",
        "consultation_fee",
        "is_active",
    )
    list_filter = ("department", "is_active", "accepts_walk_ins")
    search_fields = ("full_name", "designation", "qualifications")
    prepopulated_fields = {"slug": ("full_name",)}
    inlines = [DoctorAvailabilityInline]
    autocomplete_fields = ["department"]
