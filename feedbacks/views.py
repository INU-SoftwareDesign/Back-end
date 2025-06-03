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
    FeedbackNestedSerializer,
)
from utils.slack import send_success_slack, send_error_slack
from datetime import datetime
from django.core.cache import cache  # ← 캐시 사용을 위해 import 추가


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
            # 캐시 키 생성: 피드백을 조회하는 학생 학번
            cache_key = f"feedbacks:student:{student_id}"
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response({"success": True, "data": cached_data}, status=status.HTTP_200_OK)

            groups = FeedbackGroup.objects.filter(student=student).order_by("grade", "class_number")
            serializer = FeedbackGroupSerializer(groups, many=True)
            data = serializer.data

            # 조회 결과를 캐시에 저장 (5분 동안 유지)
            cache.set(cache_key, data, timeout=300)

            send_success_slack(request, "피드백 조회", start_time)
            return Response({"success": True, "data": data}, status=status.HTTP_200_OK)

        except Exception as e:
            send_error_slack(request, "피드백 조회", start_time, error=e)
            return Response(
                {"success": False, "error": {"code": "SERVER_ERROR", "message": "서버 오류가 발생했습니다."}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FeedbackCreateView(APIView):
    """
    2. 피드백 생성 (POST /feedbacks/)
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

            # 피드백 생성 시 해당 학생 학번을 가져와 캐시 삭제
            student_id = group.student.student_id
            cache.delete(f"feedbacks:student:{student_id}")

            send_success_slack(request, "피드백 생성", start_time)
            return Response(
                {"success": True, "data": output_serializer.data},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            send_error_slack(request, "피드백 생성", start_time, error=e)
            return Response(
                {"success": False, "error": {"code": "SERVER_ERROR", "message": "서버 오류가 발생했습니다."}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FeedbackDetailView(APIView):
    """
    3. 피드백 그룹 전체 수정 (PATCH /feedbacks/groups/<group_id>/)
    4. 피드백 삭제 (DELETE /feedbacks/<feedback_id>/)
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request, group_id):
        start_time = datetime.now()
        try:
            # 1) 그룹이 실제 존재하는지 확인
            try:
                group = FeedbackGroup.objects.get(id=group_id)
            except FeedbackGroup.DoesNotExist:
                send_error_slack(request, "피드백 그룹 수정", start_time, error=Exception("피드백 그룹을 찾을 수 없습니다."))
                return Response(
                    {"success": False, "message": "피드백 그룹을 찾을 수 없습니다."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # 2) 요청 바디에서 feedbacks 배열 추출
            feedbacks_data = request.data.get("feedbacks")
            if not isinstance(feedbacks_data, list) or len(feedbacks_data) == 0:
                send_error_slack(request, "피드백 그룹 수정", start_time, error=Exception("feedbacks 배열이 필요합니다."))
                return Response(
                    {"success": False, "message": "feedbacks 배열이 필요합니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 3) 기존 Feedback들은 모두 삭제
            group.feedbacks.all().delete()

            # 4) 새로운 Feedback 항목들을 group에 추가
            for item in feedbacks_data:
                category = item.get("category")
                content = item.get("content")
                if not category or content is None or str(content).strip() == "":
                    raise ValueError("각 피드백 항목은 category와 content가 필요합니다.")
                Feedback.objects.create(
                    feedback_group=group,
                    category=category,
                    content=content
                )

            # 5) 그룹(updated_at)을 갱신
            group.save()

            # 6) 수정 후, 전체 그룹 정보를 직렬화해서 반환
            serializer = FeedbackGroupSerializer(group)
            data = serializer.data

            # 7) 해당 학생(student_id)의 캐시 삭제
            student_id = group.student.student_id
            cache.delete(f"feedbacks:student:{student_id}")

            send_success_slack(request, "피드백 그룹 전체 수정", start_time)
            return Response({"success": True, "data": data}, status=status.HTTP_200_OK)

        except ValueError as ve:
            send_error_slack(request, "피드백 그룹 수정", start_time, error=ve)
            return Response(
                {"success": False, "message": str(ve)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            send_error_slack(request, "피드백 그룹 수정", start_time, error=e)
            return Response(
                {"success": False, "error": {"code": "SERVER_ERROR", "message": "서버 오류가 발생했습니다."}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            student_id = group.student.student_id  # 삭제 전 학생 학번 저장
            feedback.delete()

            if not group.feedbacks.exists():
                group.delete()

            # 피드백 삭제 시 해당 학생 학번을 사용해 캐시 삭제
            cache.delete(f"feedbacks:student:{student_id}")

            send_success_slack(request, "피드백 삭제", start_time)
            return Response(
                {"success": True, "message": "피드백이 성공적으로 삭제되었습니다."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            send_error_slack(request, "피드백 삭제", start_time, error=e)
            return Response(
                {"success": False, "error": {"code": "SERVER_ERROR", "message": "서버 오류가 발생했습니다."}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
