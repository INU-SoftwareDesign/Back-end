from rest_framework import serializers
from .models import Student
from accounts.models import User
from classrooms.models import Classroom

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email', 'phone']

class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'grade', 'class_number']

class StudentListSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    classroom = ClassroomSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'user', 'student_number', 'classroom']

class StudentDetailSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    classroom = ClassroomSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'user', 'student_number', 'special_note', 'classroom']
