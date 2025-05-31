from django.urls import path
from .views import (
    StudentSpecialNoteListView,
    SpecialNoteCreateView,
    SpecialNoteDetailView,
)

urlpatterns = [
    path("students/<str:student_id>", StudentSpecialNoteListView.as_view(), name="specialnote_student_list"),
    path("", SpecialNoteCreateView.as_view(), name="specialnote_create"),
    path("<int:note_id>", SpecialNoteDetailView.as_view(), name="specialnote_detail"),
]
