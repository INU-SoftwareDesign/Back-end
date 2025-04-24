from django.db import models
from students.models import Student
from subjects.models import Subject

class GradeGroup(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    grade = models.CharField(max_length=10)
    semester = models.CharField(max_length=10)
    grade_status = models.CharField(max_length=20, choices=[
        ('입력완료', '입력완료'),
        ('임시저장', '임시저장'),
        ('미입력', '미입력')
    ])
    updated_at = models.DateTimeField()

class Grade(models.Model):
    grade_group = models.ForeignKey(GradeGroup, related_name='grades', on_delete=models.CASCADE, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    credits = models.PositiveSmallIntegerField()
    midterm = models.FloatField()
    final = models.FloatField()
    performance = models.FloatField()
    total_score = models.FloatField()
