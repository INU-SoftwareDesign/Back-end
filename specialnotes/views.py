from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from datetime import datetime

from .models import SpecialNote
from .serializers import (
    SpecialNoteSerializer,
    SpecialNoteCreateSerializer,
    SpecialNoteUpdateSerializer,
)
from students.models import Student
from teachers.models import Teacher
from utils.slack import send_success_slack, send_error_slack


class StudentSpecialNoteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        start_time = datetime.now()
        try:
            student = get_object_or_404(Student, student_id=student_id)
            notes = SpecialNote.objects.filter(student=student).order_by("grade", "class_number")
            serializer = SpecialNoteSerializer(notes, many=True)
            send_success_slack(request, "특기사항 조회", start_time)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            send_error_slack(request, "특기사항 조회", start_time, error=e)
            return Response(
                {"success": False, "error": {"code": "SERVER_ERROR", "message": "서버 오류가 발생했습니다."}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SpecialNoteCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        start_time = datetime.now()
        try:
            serializer = SpecialNoteCreateSerializer(data=request.data)
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

                send_error_slack(request, "특기사항 생성", start_time, error=Exception("필수 필드 누락 또는 잘못됨"))
                return Response(
                    {
                        "success": False,
                        "message": "필수 필드가 누락되었거나 잘못되었습니다.",
                        "errors": errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            note_obj = serializer.save()
            output_serializer = SpecialNoteSerializer(note_obj)
            send_success_slack(request, "특기사항 생성", start_time)
            return Response({"success": True, "data": output_serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            send_error_slack(request, "특기사항 생성", start_time, error=e)
            return Response(
                {"success": False, "error": {"code": "SERVER_ERROR", "message": "서버 오류가 발생했습니다."}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SpecialNoteDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, note_id):
        start_time = datetime.now()
        try:
            note_obj = get_object_or_404(SpecialNote, id=note_id)
            serializer = SpecialNoteUpdateSerializer(data=request.data)
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

                send_error_slack(request, "특기사항 수정", start_time, error=Exception("필수 필드 누락 또는 잘못됨"))
                return Response(
                    {
                        "success": False,
                        "message": "필수 필드가 누락되었거나 잘못되었습니다.",
                        "errors": errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 업데이트 로직, instance와 validated_data 전달
            note_obj = serializer.update(note_obj, serializer.validated_data)
            output_serializer = SpecialNoteSerializer(note_obj)
            send_success_slack(request, "특기사항 수정", start_time)
            return Response({"success": True, "data": output_serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            send_error_slack(request, "특기사항 수정", start_time, error=e)
            return Response(
                {"success": False, "error": {"code": "SERVER_ERROR", "message": "서버 오류가 발생했습니다."}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, note_id):
        start_time = datetime.now()
        try:
            note_obj = get_object_or_404(SpecialNote, id=note_id)
            note_obj.delete()
            send_success_slack(request, "특기사항 삭제", start_time)
            return Response(
                {"success": True, "message": "특기사항이 성공적으로 삭제되었습니다."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            send_error_slack(request, "특기사항 삭제", start_time, error=e)
            return Response(
                {"success": False, "error": {"code": "SERVER_ERROR", "message": "서버 오류가 발생했습니다."}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
