from django.urls import path
from . import views

urlpatterns = [
    path('', views.TeacherView.as_view()),
    path('<int:pk>/', views.TeacherDetailView.as_view()),
]
