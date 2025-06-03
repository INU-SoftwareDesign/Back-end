# feedbacks/urls.py

from django.urls import path
from .views import (
    StudentFeedbackListView,    # GET /feedbacks/students/<student_id>/
    FeedbackCreateView,         # POST /feedbacks/
    FeedbackDetailView,         # DELETE /feedbacks/<feedback_id>/
    FeedbackDetailView as FeedbackGroupUpdateView  # PATCH /feedbacks/groups/<group_id>/
)

urlpatterns = [
    path("students/<str:student_id>", StudentFeedbackListView.as_view(), name="feedback_student_list"),
    path("", FeedbackCreateView.as_view(), name="feedback_create"),
    # 그룹 전체 덮어쓰기용 (PATCH)
    path("groups/<int:group_id>", FeedbackDetailView.as_view(), name="feedback_group_update"),
    # 개별 피드백 삭제용 (DELETE)
    path("<int:feedback_id>", FeedbackDetailView.as_view(), name="feedback_detail"),
]
