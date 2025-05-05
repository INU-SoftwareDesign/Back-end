from django.urls import path
from . import views

urlpatterns = [
    path('management-status', views.GradeManagementStatusView.as_view(), name='grade-management-status'),
    path('students/<int:student_id>/overview', views.GradeOverviewView.as_view(), name='grade-overview'),
    path('students/<int:student_id>', views.GradeUpdateView.as_view(), name='grade-update'),
]
