from django.db import models
from students.models import Student
from teachers.models import Teacher


class FeedbackGroup(models.Model):
    """학년·반별로 묶인 피드백 블록"""
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="feedback_groups"
    )
    grade = models.PositiveSmallIntegerField()
    class_number = models.PositiveSmallIntegerField()
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, related_name="feedback_groups"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.student_id} - {self.grade}학년 {self.class_number}반"


class Feedback(models.Model):
    """단일 피드백 항목"""
    CATEGORY_CHOICES = [
        ("academic", "Academic"),
        ("behavior", "Behavior"),
        ("attendance", "Attendance"),
        ("attitude", "Attitude"),
    ]

    feedback_group = models.ForeignKey(
        FeedbackGroup, on_delete=models.CASCADE, related_name="feedbacks"
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.feedback_group.student.student_id} - {self.category}"
