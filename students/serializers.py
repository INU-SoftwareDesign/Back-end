from rest_framework import serializers
from .models import Student, StudentClassHistory, StudentAcademicRecord
from consultations.models import Counseling
from parents.models import ParentStudent

class StudentListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    studentId = serializers.CharField(source='student_id')
    grade = serializers.SerializerMethodField()
    classNumber = serializers.SerializerMethodField()
    number = serializers.IntegerField(source='student_number')
    recentCounselingDate = serializers.SerializerMethodField()
    profileImage = serializers.URLField(source='profile_image')

    class Meta:
        model = Student
        fields = ['id', 'name', 'studentId', 'grade', 'classNumber', 'number', 'recentCounselingDate', 'profileImage']

    def get_grade(self, obj):
        return obj.classroom.grade if obj.classroom else None

    def get_classNumber(self, obj):
        return obj.classroom.class_number if obj.classroom else None

    def get_recentCounselingDate(self, obj):
        latest = Counseling.objects.filter(student=obj).order_by('-counseling_date').first()
        return latest.counseling_date if latest else None


class StudentClassHistorySerializer(serializers.ModelSerializer):
    classNumber = serializers.IntegerField(source='class_number')

    class Meta:
        model = StudentClassHistory
        fields = ['grade', 'classNumber', 'number', 'homeroom_teacher']


class StudentDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    studentId = serializers.CharField(source='student_id')
    grade = serializers.SerializerMethodField()
    classNumber = serializers.SerializerMethodField()
    number = serializers.IntegerField(source='student_number')
    birthDate = serializers.DateField(source='user.birth_date')
    address = serializers.CharField(source='user.address')
    fatherName = serializers.SerializerMethodField()
    motherName = serializers.SerializerMethodField()
    history = StudentClassHistorySerializer(many=True, read_only=True)
    academicRecords = serializers.SerializerMethodField()
    profileImage = serializers.URLField(source='profile_image')

    class Meta:
        model = Student
        fields = [
            'profileImage', 'name', 'studentId', 'grade', 'classNumber', 'number',
            'birthDate', 'address', 'fatherName', 'motherName', 'history', 'academicRecords'
        ]

    def get_grade(self, obj):
        return obj.classroom.grade if obj.classroom else None

    def get_classNumber(self, obj):
        return obj.classroom.class_number if obj.classroom else None

    def get_fatherName(self, obj):
        ps = obj.parentstudent_set.filter(role='father').select_related('parent__user').first()
        return ps.parent.user.name if ps else None

    def get_motherName(self, obj):
        ps = obj.parentstudent_set.filter(role='mother').select_related('parent__user').first()
        return ps.parent.user.name if ps else None

    def get_academicRecords(self, obj):
        return [record.description for record in obj.academic_records.all()]

class StudentClassHistoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClassHistory
        fields = ['grade', 'class_number', 'number', 'homeroom_teacher']

class StudentAcademicRecordWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAcademicRecord
        fields = ['description']

class StudentUpdateSerializer(serializers.ModelSerializer):
    history = StudentClassHistoryWriteSerializer(many=True)
    academicRecords = StudentAcademicRecordWriteSerializer(many=True, source='academic_records')

    class Meta:
        model = Student
        fields = ['student_id', 'student_number', 'classroom', 'profile_image', 'history', 'academicRecords']

    def update(self, instance, validated_data):
        history_data = validated_data.pop('history', None)
        academic_data = validated_data.pop('academic_records', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if history_data is not None:
            instance.history.all().delete()
            for history in history_data:
                StudentClassHistory.objects.create(student=instance, **history)

        if academic_data is not None:
            instance.academic_records.all().delete()
            for record in academic_data:
                StudentAcademicRecord.objects.create(student=instance, **record)

        return instance
