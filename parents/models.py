from django.db import models
from accounts.models import User
from students.models import Student

# Create your models here.
class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student, through='ParentStudent')

class ParentStudent(models.Model):
    ROLE_CHOICES = (
        ('father', 'Father'),
        ('mother', 'Mother'),
    )
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)