from rest_framework import serializers
from .models import Student
from accounts.models import User
from classrooms.models import Classroom

class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'grade', 'class_number']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email', 'phone']

class StudentDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    classroom = ClassroomSerializer()

    class Meta:
        model = Student
        fields = ['id', 'user', 'student_number', 'special_note', 'classroom']

    def update(self, instance, validated_data):
        classroom_data = validated_data.pop('classroom', None)
        if classroom_data:
            classroom = Classroom.objects.filter(
                grade=classroom_data['grade'],
                class_number=classroom_data['class_number']
            ).first()
            if classroom:
                instance.classroom = classroom
        return super().update(instance, validated_data)

class StudentListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name', read_only=True)
    classroom = ClassroomSerializer()

    class Meta:
        model = Student
        fields = ['id', 'name', 'student_number', 'classroom']
