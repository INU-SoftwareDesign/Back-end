from django.db import models
from students.models import Student
from teachers.models import Teacher

class AttendanceRecord(models.Model):
    ATTENDANCE_TYPE_CHOICES = [
        ('absence', '결석'),
        ('lateness', '지각'),
        ('earlyLeave', '조퇴'),
        ('result', '결과'),
    ]

    REASON_TYPE_CHOICES = [
        ('illness', '질병'),
        ('unauthorized', '미인정'),
        ('etc', '기타'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    grade = models.CharField(max_length=10)
    year = models.IntegerField()
    date = models.DateField()
    attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPE_CHOICES)
    reason_type = models.CharField(max_length=20, choices=REASON_TYPE_CHOICES)
    reason = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'grade', 'year', 'attendance_type', 'reason_type', 'date')

class AttendanceSummary(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    grade = models.CharField(max_length=10)
    year = models.IntegerField()
    home_teacher = models.CharField(max_length=50)
    total_days = models.IntegerField(default=0)
    remarks = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'grade', 'year')
