from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="home"),
    path(
        "notifications/<int:pk>/read/",
        views.MarkNotificationReadView.as_view(),
        name="mark_notification_read",
    ),
]
