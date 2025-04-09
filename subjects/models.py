from django.db import models
from teachers.models import Teacher

# Create your models here.

class Subject(models.Model):
    name = models.CharField(max_length=50)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)