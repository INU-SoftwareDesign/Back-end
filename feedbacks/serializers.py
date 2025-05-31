from rest_framework import serializers
from django.db import transaction

from .models import FeedbackGroup, Feedback
from students.models import Student
from teachers.models import Teacher


class FeedbackNestedSerializer(serializers.ModelSerializer):
    """
    단일 Feedback 항목을 직렬화
    """
    id = serializers.IntegerField()
    category = serializers.CharField()
    content = serializers.CharField()

    class Meta:
        model = Feedback
        fields = ("id", "category", "content")


class FeedbackGroupSerializer(serializers.ModelSerializer):
    """
    FeedbackGroup을 스펙에 맞춰 출력
    - studentId는 Student.student_id (학번)으로 변경
    """
    id = serializers.IntegerField()  # FeedbackGroup PK
    studentId = serializers.CharField(source="student.student_id")  # 학번으로 변경
    grade = serializers.CharField()
    classNumber = serializers.CharField(source="class_number")
    teacherId = serializers.IntegerField(source="teacher.id")
    teacherName = serializers.CharField(source="teacher.user.name")
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")
    feedbacks = FeedbackNestedSerializer(many=True)

    class Meta:
        model = FeedbackGroup
        fields = (
            "id",
            "studentId",
            "grade",
            "classNumber",
            "teacherId",
            "teacherName",
            "createdAt",
            "updatedAt",
            "feedbacks",
        )


class FeedbackCreateNestedSerializer(serializers.Serializer):
    """
    요청 본문 중, 각 피드백 항목 내부 구조
    """
    category = serializers.ChoiceField(choices=Feedback.CATEGORY_CHOICES)
    content = serializers.CharField()


class CreateFeedbackSerializer(serializers.Serializer):
    """
    새로운 FeedbackGroup(학년·반별 묶음)과 Feedback 항목들을 생성할 때 사용
    - studentId: Student.student_id (학번, 문자열) 로 받도록 변경
    """
    studentId = serializers.CharField()       # 학번(문자열)으로 수정
    grade = serializers.CharField()
    classNumber = serializers.CharField()
    teacherId = serializers.IntegerField()
    teacherName = serializers.CharField()
    feedbacks = FeedbackCreateNestedSerializer(many=True)

    def validate_studentId(self, value):
        """
        studentId → Student.student_id(학번)으로 조회
        """
        try:
            student = Student.objects.get(student_id=value)
        except Student.DoesNotExist:
            raise serializers.ValidationError("학생을 찾을 수 없습니다.")
        return student

    def validate_teacherId(self, value):
        """
        teacherId → Teacher PK(id)로 조회
        """
        try:
            teacher = Teacher.objects.get(id=value)
        except Teacher.DoesNotExist:
            raise serializers.ValidationError("교사를 찾을 수 없습니다.")
        return teacher

    def validate(self, data):
        """
        teacherName이 실제 교사 이름(teacher.user.name)과 일치하는지 검증
        """
        teacher = data.get("teacherId")
        teacher_name_input = data.get("teacherName")
        actual_name = teacher.user.name
        if teacher_name_input != actual_name:
            raise serializers.ValidationError({
                "teacherName": "요청에 포함된 teacherName이 실제 교사 이름과 일치하지 않습니다."
            })
        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        검증된 데이터로 FeedbackGroup 및 Feedback 항목 생성
        """
        # 1) student, grade, classNumber, teacher 객체 꺼내기
        student = validated_data.pop("studentId")       # 실제 Student 인스턴스 (학번으로 조회됨)
        grade = validated_data.pop("grade")
        class_number = validated_data.pop("classNumber")
        teacher = validated_data.pop("teacherId")       # 실제 Teacher 인스턴스
        validated_data.pop("teacherName")                # teacherName 검증 후 사용 안 함

        # 2) 동일 조합의 FeedbackGroup이 이미 있는지 조회 (최신 순으로 하나만 선택)
        existing_groups = FeedbackGroup.objects.filter(
            student=student,
            grade=grade,
            class_number=class_number,
            teacher=teacher
        ).order_by("-created_at")

        if existing_groups.exists():
            group = existing_groups.first()
        else:
            group = FeedbackGroup.objects.create(
                student=student,
                grade=grade,
                class_number=class_number,
                teacher=teacher
            )

        # 3) 새 Feedback 항목을 (반드시) 위 group에 추가
        for fb in validated_data.pop("feedbacks"):
            Feedback.objects.create(
                feedback_group=group,
                category=fb["category"],
                content=fb["content"]
            )

        return group
