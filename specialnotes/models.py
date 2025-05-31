from django.db import models
from students.models import Student
from teachers.models import Teacher


class SpecialNote(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="special_notes")
    grade = models.PositiveSmallIntegerField()
    class_number = models.PositiveSmallIntegerField()

    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name="special_notes")
    teacher_name = models.CharField(max_length=100)

    special_talent = models.CharField(max_length=255)
    career_aspiration = models.JSONField()
    note = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"SpecialNote(id={self.id}, student={self.student.student_id}, grade={self.grade}, class={self.class_number})"
