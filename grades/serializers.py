from rest_framework import serializers
from .models import GradeGroup, Grade
from students.models import Student

class GradeStudentStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='user.name')
    studentId = serializers.CharField(source='student_id')
    grade = serializers.SerializerMethodField()
    class_ = serializers.SerializerMethodField()
    number = serializers.IntegerField(source='student_number')
    profileImage = serializers.URLField(source='profile_image')
    gradeStatus = serializers.CharField()

    def get_grade(self, obj):
        return obj.classroom.grade if obj.classroom else None

    def get_class_(self, obj):
        return obj.classroom.class_number if obj.classroom else None

class GradeInputSerializer(serializers.Serializer):
    grade = serializers.CharField()
    semester = serializers.CharField()
    gradeStatus = serializers.ChoiceField(choices=['입력완료', '임시저장', '미입력'])
    updatedAt = serializers.DateTimeField()
    subjects = serializers.ListField(child=serializers.DictField())