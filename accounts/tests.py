# accounts/tests.py

from django.test import SimpleTestCase
from django.urls import resolve
from accounts.serializers import UserSerializer
from accounts.views import (
    SignUpView,
    LoginView,
    LogoutView,
    ChangePasswordView,
    UserProfileView,
    SocialLoginView,
    SocialRegisterDetailView,
)


class UserSerializerBasicTest(SimpleTestCase):
    def test_user_serializer_fields(self):
        """
        UserSerializer에 정의된 Meta.fields가 올바르게 설정되었는지 확인합니다.
        """
        expected_fields = {
            'id', 'username', 'role', 'name', 'email', 'phone',
            'birth_date', 'address', 'is_active', 'approval_status'
        }
        actual_fields = set(UserSerializer.Meta.fields)
        self.assertEqual(actual_fields, expected_fields)


class URLPatternsResolveTest(SimpleTestCase):
    def test_signup_url_resolves(self):
        """
        '/api/users/register' 경로가 SignUpView로 연결되는지 확인합니다.
        """
        resolver = resolve('/api/users/register')
        self.assertEqual(resolver.func.view_class, SignUpView)

    def test_login_url_resolves(self):
        """
        '/api/auth/login' 경로가 LoginView로 연결되는지 확인합니다.
        """
        resolver = resolve('/api/auth/login')
        self.assertEqual(resolver.func.view_class, LoginView)

    def test_logout_url_resolves(self):
        """
        '/api/auth/logout' 경로가 LogoutView로 연결되는지 확인합니다.
        """
        resolver = resolve('/api/auth/logout')
        self.assertEqual(resolver.func.view_class, LogoutView)

    def test_change_password_url_resolves(self):
        """
        '/api/users/change-password' 경로가 ChangePasswordView로 연결되는지 확인합니다.
        """
        resolver = resolve('/api/users/change-password')
        self.assertEqual(resolver.func.view_class, ChangePasswordView)

    def test_user_profile_url_resolves(self):
        """
        '/api/users/profile' 경로가 UserProfileView로 연결되는지 확인합니다.
        """
        resolver = resolve('/api/users/profile')
        self.assertEqual(resolver.func.view_class, UserProfileView)

    def test_social_login_url_resolves(self):
        """
        '/api/auth/login/social' 경로가 SocialLoginView로 연결되는지 확인합니다.
        """
        resolver = resolve('/api/auth/login/social')
        self.assertEqual(resolver.func.view_class, SocialLoginView)

    def test_social_register_detail_url_resolves(self):
        """
        '/api/auth/social/register-detail' 경로가 SocialRegisterDetailView로 연결되는지 확인합니다.
        """
        resolver = resolve('/api/auth/social/register-detail')
        self.assertEqual(resolver.func.view_class, SocialRegisterDetailView)
