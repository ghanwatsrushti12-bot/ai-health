from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("author", "category", "doctor", "rating", "is_published", "created_at")
    list_filter = ("category", "rating", "is_published")
    search_fields = ("message", "author__username", "doctor__full_name")
    list_editable = ("is_published",)
    date_hierarchy = "created_at"
