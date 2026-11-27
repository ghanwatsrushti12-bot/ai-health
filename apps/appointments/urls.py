from django.urls import path

from . import views

app_name = "appointments"

urlpatterns = [
    path("", views.AppointmentListView.as_view(), name="list"),
    path("book/", views.BookAppointmentView.as_view(), name="book"),
    path("available-slots/", views.AvailableSlotsView.as_view(), name="available_slots"),
    path("<int:pk>/", views.AppointmentDetailView.as_view(), name="detail"),
    path("<int:pk>/cancel/", views.CancelAppointmentView.as_view(), name="cancel"),
    path(
        "<int:pk>/status/",
        views.AppointmentStatusUpdateView.as_view(),
        name="status_update",
    ),
]
