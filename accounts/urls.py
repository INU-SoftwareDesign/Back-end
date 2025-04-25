from django.urls import path
from . import views

urlpatterns = [
    path('users/register', views.SignUpView.as_view()),
    path('auth/login', views.LoginView.as_view()),
    path('auth/logout', views.LogoutView.as_view()),
    path('users/change-password', views.ChangePasswordView.as_view()),
    path('accounts/<int:pk>/', views.UserUpdateView.as_view())
]