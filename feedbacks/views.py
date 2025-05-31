from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from students.models import Student
from teachers.models import Teacher
from .models import FeedbackGroup, Feedback
from .serializers import (
    FeedbackGroupSerializer,
    CreateFeedbackSerializer,
)


class StudentFeedbackListView(APIView):
    """
    1. 학생 피드백 조회 (GET /feedbacks/students/<student_id>/)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        try:
            # student_id: Student PK (정수)
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response(
                {"success": False, "message": "학생을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        groups = FeedbackGroup.objects.filter(student=student).order_by("grade", "class_number")
        serializer = FeedbackGroupSerializer(groups, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)


class FeedbackCreateView(APIView):
    """
    2. 피드백 생성 (POST /api/feedbacks/)
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CreateFeedbackSerializer(data=request.data)
        if not serializer.is_valid():
            # 유효성 검사 실패 시, 필드별 에러 반환
            errors = []
            for field, msgs in serializer.errors.items():
                if isinstance(msgs, dict):
                    for subfield, submsgs in msgs.items():
                        for msg in submsgs:
                            errors.append({"field": subfield, "message": str(msg)})
                else:
                    for msg in msgs:
                        errors.append({"field": field, "message": str(msg)})

            return Response(
                {
                    "success": False,
                    "message": "필수 필드가 누락되었거나 잘못되었습니다.",
                    "errors": errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        group = serializer.save()
        output_serializer = FeedbackGroupSerializer(group)
        return Response(
            {"success": True, "data": output_serializer.data},
            status=status.HTTP_201_CREATED,
        )


class FeedbackDetailView(APIView):
    """
    3. 피드백 수정 (PATCH /api/feedbacks/<feedback_id>/)
    4. 피드백 삭제 (DELETE /api/feedbacks/<feedback_id>/)
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, feedback_id):
        try:
            feedback = Feedback.objects.get(id=feedback_id)
        except Feedback.DoesNotExist:
            return Response(
                {"success": False, "message": "피드백을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        content = request.data.get("content")
        updated_at = request.data.get("updatedAt")
        if content is None or str(content).strip() == "":
            return Response(
                {
                    "success": False,
                    "message": "필수 필드가 누락되었습니다.",
                    "errors": [
                        {"field": "content", "message": "피드백 내용은 필수입니다."}
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1) 개별 Feedback의 content와 updated_at 반영
        if updated_at:
            try:
                feedback.updated_at = updated_at
            except Exception:
                pass

        feedback.content = content
        feedback.save()

        # 2) 피드백 그룹의 updated_at도 함께 갱신
        group = feedback.feedback_group
        group.save()

        # 3) 그룹 전체를 직렬화하여 반환
        serializer = FeedbackGroupSerializer(group)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, feedback_id):
        try:
            feedback = Feedback.objects.get(id=feedback_id)
        except Feedback.DoesNotExist:
            return Response(
                {"success": False, "message": "피드백을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        group = feedback.feedback_group
        feedback.delete()

        # 해당 그룹에 남아있는 피드백이 없으면 그룹도 삭제
        if not group.feedbacks.exists():
            group.delete()

        return Response(
            {"success": True, "message": "피드백이 성공적으로 삭제되었습니다."},
            status=status.HTTP_200_OK,
        )
