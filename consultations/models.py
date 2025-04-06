from django.db import models
from teachers.models import Teacher
from students.models import Student

# Create your models here.
class Consultation(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    content = models.TextField()
    next_plan = models.TextField(blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)