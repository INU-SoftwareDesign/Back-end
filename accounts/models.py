from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    birth_date = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    social_type = models.CharField(
        max_length=10, choices=[('kakao', 'Kakao'), ('google', 'Google'), ('naver', 'Naver')],
        blank=True, null=True
    )
    social_id = models.CharField(max_length=100, blank=True, null=True, unique=True)

    is_active = models.BooleanField(default=False)
    approval_status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )