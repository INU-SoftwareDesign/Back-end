from rest_framework import serializers
from .models import Consultation
from students.models import Student
from teachers.models import Teacher

class StudentSimpleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'name']

class TeacherSimpleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'name']

class ConsultationSerializer(serializers.ModelSerializer):
    student = StudentSimpleSerializer(read_only=True)
    teacher = TeacherSimpleSerializer(read_only=True)

    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source='student', write_only=True
    )
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(), source='teacher', write_only=True
    )

    class Meta:
        model = Consultation
        fields = [
            'id', 'student', 'student_id',
            'teacher', 'teacher_id',
            'date', 'content', 'next_plan'
        ]
