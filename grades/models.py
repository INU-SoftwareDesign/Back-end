from django.db import models
from students.models import Student
from subjects.models import Subject

# Create your models here.

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.CharField(max_length=20)
    score = models.FloatField()