from django.db import models
from accounts.models import User
from classrooms.models import Classroom

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True)
    student_number = models.PositiveSmallIntegerField()
    special_note = models.TextField(blank=True, null=True)
