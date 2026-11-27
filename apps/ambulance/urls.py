from django.urls import path

from . import views

app_name = "ambulance"

urlpatterns = [
    path("request/", views.AmbulanceRequestCreateView.as_view(), name="request_create"),
    path(
        "request/success/",
        views.AmbulanceRequestSuccessView.as_view(),
        name="request_success",
    ),
    path("", views.AmbulanceRequestListView.as_view(), name="request_list"),
    path(
        "<int:pk>/update/",
        views.AmbulanceRequestUpdateView.as_view(),
        name="request_update",
    ),
]
