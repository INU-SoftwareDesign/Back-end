from rest_framework import serializers
from accounts.models import User
from classrooms.models import Classroom
from subjects.models import Subject
from .models import Teacher

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email', 'phone']

class ClassroomSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'grade', 'class_number']

class SubjectSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']

class TeacherListSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    classroom = ClassroomSimpleSerializer(read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'classroom']

class TeacherDetailSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    classroom = ClassroomSimpleSerializer(read_only=True)
    subjects = SubjectSimpleSerializer(source='subject_set', many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'classroom', 'subjects']

class TeacherUpdateSerializer(serializers.ModelSerializer):
    classroom_id = serializers.PrimaryKeyRelatedField(
        queryset=Classroom.objects.all(), required=False, write_only=True
    )
    subject_ids = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), many=True, required=False, write_only=True
    )

    user = UserDetailSerializer(read_only=True)
    classroom = ClassroomSimpleSerializer(read_only=True)
    subjects = SubjectSimpleSerializer(source='subject_set', many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = [
            'id', 'user',
            'classroom_id', 'subject_ids',
            'classroom', 'subjects'
        ]

    def update(self, instance, validated_data):
        from classrooms.models import Classroom
        classroom = validated_data.pop('classroom_id', None)
        subject_list = validated_data.pop('subject_ids', [])

        Classroom.objects.filter(teacher=instance).update(teacher=None)

        from subjects.models import Subject
        Subject.objects.filter(teacher=instance).update(teacher=None)

        if classroom:
            classroom.teacher = instance
            classroom.save()

        for subject in subject_list:
            subject.teacher = instance
            subject.save()

        return instance
