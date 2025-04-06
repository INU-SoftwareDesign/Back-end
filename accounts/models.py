from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)