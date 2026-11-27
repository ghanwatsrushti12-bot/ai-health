from django.urls import path

from . import views

app_name = "doctors"

urlpatterns = [
    path("", views.DoctorListView.as_view(), name="doctor_list"),
    path("departments/", views.DepartmentListView.as_view(), name="department_list"),
    path(
        "departments/<slug:slug>/",
        views.DepartmentDetailView.as_view(),
        name="department_detail",
    ),
    path("manage/", views.DoctorManageListView.as_view(), name="manage_list"),
    path("manage/new/", views.DoctorCreateView.as_view(), name="doctor_create"),
    path(
        "manage/<int:pk>/",
        views.DoctorManageDetailView.as_view(),
        name="manage_detail",
    ),
    path(
        "manage/<int:pk>/edit/",
        views.DoctorUpdateView.as_view(),
        name="doctor_update",
    ),
    path(
        "manage/<int:pk>/delete/",
        views.DoctorDeleteView.as_view(),
        name="doctor_delete",
    ),
    path(
        "manage/<int:doctor_id>/availability/new/",
        views.DoctorAvailabilityCreateView.as_view(),
        name="availability_create",
    ),
    path(
        "manage/availability/<int:pk>/delete/",
        views.delete_availability_slot,
        name="availability_delete",
    ),
    path("<slug:slug>/", views.DoctorDetailView.as_view(), name="doctor_detail"),
]
