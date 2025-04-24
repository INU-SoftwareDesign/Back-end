from django.db import models
from accounts.models import User
from classrooms.models import Classroom

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True)
    student_number = models.PositiveSmallIntegerField()
    student_id = models.CharField(max_length=20, unique=True)
    profile_image = models.URLField(blank=True, null=True, default='https://cdn-icons-png.flaticon.com/512/8847/8847419.png')

class StudentClassHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='history')
    grade = models.PositiveSmallIntegerField()
    class_number = models.PositiveSmallIntegerField()
    number = models.PositiveSmallIntegerField()
    homeroom_teacher = models.CharField(max_length=50)

class StudentAcademicRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='academic_records')
    description = models.CharField(max_length=255)
