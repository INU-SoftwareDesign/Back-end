from django.urls import path
from . import views

urlpatterns = [
    path('student/<int:student_id>', views.StudentCounselingListView.as_view()),
    path('teacher/<int:teacher_id>/requests', views.TeacherCounselingRequestListView.as_view()),
    path('teacher/<int:teacher_id>/scheduled', views.TeacherScheduledCounselingListView.as_view()),
    path('teacher/<int:teacher_id>/calendar', views.TeacherCounselingCalendarView.as_view()),
    path('available-times', views.AvailableCounselingTimesView.as_view()),
    path('request', views.CounselingRequestCreateView.as_view()),
    path('<int:counseling_id>/approve', views.CounselingApproveView.as_view()),
    path('<int:counseling_id>', views.CounselingUpdateCancelView.as_view()),
]
