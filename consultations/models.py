from django.db import models
from students.models import Student
from teachers.models import Teacher

class Counseling(models.Model):
    COUNSELING_TYPE_CHOICES = [
        ('교수상담', '교수상담'),
        ('글쓰기상담', '글쓰기상담'),
    ]

    COUNSELING_CATEGORY_CHOICES = [
        ('학업', '학업'),
        ('진로', '진로'),
        ('심리', '심리'),
    ]

    STATUS_CHOICES = [
        ('신청', '신청'),
        ('대기', '대기'),
        ('예약확정', '예약확정'),
        ('완료', '완료'),
        ('취소', '취소'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='counselings')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='counselings')
    request_date = models.DateField(auto_now_add=True)
    counseling_date = models.DateField()
    counseling_time = models.TimeField()
    counseling_type = models.CharField(max_length=20, choices=COUNSELING_TYPE_CHOICES)
    counseling_category = models.CharField(max_length=20, choices=COUNSELING_CATEGORY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='신청')
    location = models.CharField(max_length=100, blank=True, null=True)
    request_content = models.TextField()
    result_content = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=20)

    class Meta:
        ordering = ['-counseling_date', '-counseling_time']
