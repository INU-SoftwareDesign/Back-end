# feedbacks/views.py

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
from utils.slack import send_success_slack, send_error_slack
from datetime import datetime


class StudentFeedbackListView(APIView):
    """
    1. 학생 피드백 조회 (GET /feedbacks/students/<student_id>/)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        start_time = datetime.now()
        try:
            # student_id: 학번(Student.student_id)
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            send_error_slack(request, "피드백 조회", start_time, error=Exception("학생을 찾을 수 없습니다."))
            return Response(
                {"success": False, "message": "학생을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            groups = FeedbackGroup.objects.filter(student=student).order_by("grade", "class_number")
            serializer = FeedbackGroupSerializer(groups, many=True)
            send_success_slack(request, "피드백 조회", start_time)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            send_error_slack(request, "피드백 조회", start_time, error=e)
            return Response({"success": False, "error": {"code": "SERVER_ERROR", "message": "서버 오류가 발생했습니다."}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FeedbackCreateView(APIView):
    """
    2. 피드백 생성 (POST /api/feedbacks/)
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        start_time = datetime.now()
        try:
            serializer = CreateFeedbackSerializer(data=request.data)
            if not serializer.is_valid():
                errors = []
                for field, msgs in serializer.errors.items():
                    if isinstance(msgs, dict):
                        for subfield, submsgs in msgs.items():
                            for msg in submsgs:
                                errors.append({"field": subfield, "message": str(msg)})
                    else:
                        for msg in msgs:
                            errors.append({"field": field, "message": str(msg)})

                send_error_slack(request, "피드백 생성", start_time, error=Exception("필수 필드 누락 또는 잘못됨"))
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
            send_success_slack(request, "피드백 생성", start_time)
            return Response(
                {"success": True, "data": output_serializer.data},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            send_error_slack(request, "피드백 생성", start_time, error=e)
            return Response({"success": False, "error": {"code": "SERVER_ERROR", "message": "서버 오류가 발생했습니다."}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FeedbackDetailView(APIView):
    """
    3. 피드백 수정 (PATCH /api/feedbacks/<feedback_id>/)
    4. 피드백 삭제 (DELETE /api/feedbacks/<feedback_id>/)
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, feedback_id):
        start_time = datetime.now()
        try:
            feedback = Feedback.objects.get(id=feedback_id)
        except Feedback.DoesNotExist:
            send_error_slack(request, "피드백 수정", start_time, error=Exception("피드백을 찾을 수 없습니다."))
            return Response(
                {"success": False, "message": "피드백을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            content = request.data.get("content")
            updated_at = request.data.get("updatedAt")
            if content is None or str(content).strip() == "":
                send_error_slack(request, "피드백 수정", start_time, error=Exception("content 필수 누락"))
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

            if updated_at:
                try:
                    feedback.updated_at = updated_at
                except Exception:
                    pass

            feedback.content = content
            feedback.save()

            # 피드백 그룹의 updated_at도 갱신
            group = feedback.feedback_group
            group.save()

            serializer = FeedbackGroupSerializer(group)
            send_success_slack(request, "피드백 수정", start_time)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            send_error_slack(request, "피드백 수정", start_time, error=e)
            return Response({"success": False, "error": {"code": "SERVER_ERROR", "message": "서버 오류가 발생했습니다."}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, feedback_id):
        start_time = datetime.now()
        try:
            feedback = Feedback.objects.get(id=feedback_id)
        except Feedback.DoesNotExist:
            send_error_slack(request, "피드백 삭제", start_time, error=Exception("피드백을 찾을 수 없습니다."))
            return Response(
                {"success": False, "message": "피드백을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            group = feedback.feedback_group
            feedback.delete()

            if not group.feedbacks.exists():
                group.delete()

            send_success_slack(request, "피드백 삭제", start_time)
            return Response(
                {"success": True, "message": "피드백이 성공적으로 삭제되었습니다."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            send_error_slack(request, "피드백 삭제", start_time, error=e)
            return Response({"success": False, "error": {"code": "SERVER_ERROR", "message": "서버 오류가 발생했습니다."}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
