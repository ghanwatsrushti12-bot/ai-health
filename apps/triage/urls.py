from django.urls import path

from . import views

app_name = "triage"

urlpatterns = [
    path("", views.SymptomCheckerView.as_view(), name="checker"),
    path("history/", views.TriageHistoryListView.as_view(), name="history"),
]
