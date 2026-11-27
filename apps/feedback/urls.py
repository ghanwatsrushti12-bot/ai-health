from django.urls import path

from . import views

app_name = "feedback"

urlpatterns = [
    path("submit/", views.FeedbackCreateView.as_view(), name="submit"),
    path("thanks/", views.FeedbackThanksView.as_view(), name="thanks"),
    path("manage/", views.FeedbackManageListView.as_view(), name="manage_list"),
]
