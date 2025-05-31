# specialnotes/serializers.py

from rest_framework import serializers
from .models import SpecialNote
from students.models import Student
from teachers.models import Teacher


class CareerAspirationSerializer(serializers.Serializer):
    student = serializers.CharField()
    parent = serializers.CharField()


class SpecialNoteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    studentId = serializers.CharField(source="student.student_id", read_only=True)
    grade = serializers.IntegerField()
    classNumber = serializers.IntegerField(source="class_number")
    teacherId = serializers.IntegerField(source="teacher.id", read_only=True)
    teacherName = serializers.CharField(source="teacher_name")
    specialTalent = serializers.CharField(source="special_talent")
    careerAspiration = CareerAspirationSerializer(source="career_aspiration")
    note = serializers.CharField()
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = SpecialNote
        fields = (
            "id",
            "studentId",
            "grade",
            "classNumber",
            "teacherId",
            "teacherName",
            "specialTalent",
            "careerAspiration",
            "note",
            "createdAt",
            "updatedAt",
        )


class SpecialNoteCreateSerializer(serializers.Serializer):
    studentId = serializers.CharField()
    grade = serializers.IntegerField()
    classNumber = serializers.IntegerField()
    teacherId = serializers.IntegerField()
    teacherName = serializers.CharField()
    specialTalent = serializers.CharField()
    careerAspiration = CareerAspirationSerializer()
    note = serializers.CharField()

    def validate_studentId(self, value):
        try:
            student = Student.objects.get(student_id=value)
        except Student.DoesNotExist:
            raise serializers.ValidationError("학생을 찾을 수 없습니다.")
        return student

    def validate_teacherId(self, value):
        try:
            teacher = Teacher.objects.get(id=value)
        except Teacher.DoesNotExist:
            raise serializers.ValidationError("교사를 찾을 수 없습니다.")
        return teacher

    def validate(self, data):
        teacher = data.get("teacherId")
        teacher_name_input = data.get("teacherName")
        actual_name = teacher.user.name
        if teacher_name_input != actual_name:
            raise serializers.ValidationError({
                "teacherName": "요청에 포함된 teacherName이 실제 교사 이름과 일치하지 않습니다."
            })
        return data

    def create(self, validated_data):
        student = validated_data.pop("studentId")
        grade = validated_data.pop("grade")
        class_number = validated_data.pop("classNumber")
        teacher = validated_data.pop("teacherId")
        teacher_name = validated_data.pop("teacherName")
        special_talent = validated_data.pop("specialTalent")
        career_asp = validated_data.pop("careerAspiration")
        note = validated_data.pop("note")

        note_obj = SpecialNote.objects.create(
            student=student,
            grade=grade,
            class_number=class_number,
            teacher=teacher,
            teacher_name=teacher_name,
            special_talent=special_talent,
            career_aspiration=career_asp,
            note=note
        )

        return note_obj


class SpecialNoteUpdateSerializer(serializers.Serializer):
    specialTalent = serializers.CharField(required=False)
    careerAspiration = CareerAspirationSerializer(required=False)
    note = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        if "specialTalent" in validated_data:
            instance.special_talent = validated_data["specialTalent"]
        if "careerAspiration" in validated_data:
            instance.career_aspiration = validated_data["careerAspiration"]
        if "note" in validated_data:
            instance.note = validated_data["note"]
        instance.save()
        return instance
