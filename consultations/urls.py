from django.urls import path
from . import views

urlpatterns = [
    path('', views.ConsultationView.as_view()),
    path('<int:pk>/', views.ConsultationDetailView.as_view()),
]
