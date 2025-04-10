from rest_framework import serializers
from .models import Attendance
from students.models import Student

class StudentSimpleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'name']

class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSimpleSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        source='student',
        write_only=True
    )

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_id', 'date', 'status', 'note']

class AttendanceListSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    attendances = serializers.ListField(child=serializers.DictField())
