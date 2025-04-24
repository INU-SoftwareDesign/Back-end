from django.urls import path
from . import views

urlpatterns = [
    path('students/<int:student_id>', views.AttendanceView.as_view(), name='attendance-manage'),
]
