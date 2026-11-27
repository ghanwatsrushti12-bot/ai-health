"""Root URL configuration for the CarePulse project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls", namespace="core")),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
    path("doctors/", include("apps.doctors.urls", namespace="doctors")),
    path("appointments/", include("apps.appointments.urls", namespace="appointments")),
    path("triage/", include("apps.triage.urls", namespace="triage")),
    path("ambulance/", include("apps.ambulance.urls", namespace="ambulance")),
    path("feedback/", include("apps.feedback.urls", namespace="feedback")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers (see apps/core/views.py)
handler404 = "apps.core.views.error_404"
handler500 = "apps.core.views.error_500"
handler403 = "apps.core.views.error_403"
handler400 = "apps.core.views.error_400"
