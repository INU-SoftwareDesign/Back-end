from django.db import models
from teachers.models import Teacher

class Classroom(models.Model):
    grade = models.PositiveSmallIntegerField()
    class_number = models.PositiveSmallIntegerField()
    teacher = models.OneToOneField(Teacher, on_delete=models.SET_NULL, null=True, blank=True)

