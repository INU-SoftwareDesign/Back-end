from django.urls import path
from .views import (
    StudentFeedbackListView,  # GET /feedbacks/students/<student_id>/
    FeedbackCreateView,       # POST /feedbacks/
    FeedbackDetailView,       # PATCH/DELETE /feedbacks/<feedback_id>/
)

urlpatterns = [
    path("students/<int:student_id>", StudentFeedbackListView.as_view(), name="feedback_student_list"),
    path("", FeedbackCreateView.as_view(), name="feedback_create"),
    path("<int:feedback_id>", FeedbackDetailView.as_view(), name="feedback_detail"),
]
