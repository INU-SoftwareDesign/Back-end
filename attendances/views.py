# attendances/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import AttendanceRecord, AttendanceSummary
from students.models import Student
from .serializers import AttendanceListResponseSerializer
from django.db.models import Q
from collections import defaultdict
from rest_framework.permissions import IsAuthenticated
from utils.slack import send_success_slack, send_error_slack
from datetime import datetime
from django.core.cache import cache

class AttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        start_time = datetime.now()
        try:
            grade = request.GET.get("grade")
            year = request.GET.get("year")

            # 캐시 키 생성: student_id, grade, year 조합을 사용
            cache_key = f"attendance:{student_id}:{grade or 'all'}:{year or 'all'}"
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)

            student = get_object_or_404(Student, id=student_id)
            summaries = AttendanceSummary.objects.filter(student=student)

            if grade and year:
                summaries = summaries.filter(grade=grade, year=year)

            attendance_data = []
            for summary in summaries:
                records = AttendanceRecord.objects.filter(
                    student=student,
                    grade=summary.grade,
                    year=summary.year
                )

                stat = defaultdict(lambda: {"illness": 0, "unauthorized": 0, "etc": 0})
                detail = defaultdict(lambda: defaultdict(list))

                for record in records:
                    typ = record.attendance_type
                    reason = record.reason_type
                    stat[typ][reason] += 1
                    detail[typ][reason].append({
                        "date": record.date,
                        "reason": record.reason or ""
                    })

                attendance_data.append({
                    "grade": summary.grade,
                    "year": summary.year,
                    "homeTeacher": summary.home_teacher,
                    "totalDays": summary.total_days,
                    "remarks": summary.remarks,
                    "attendance": stat,
                    "details": detail
                })

            res = {
                "studentId": student.id,
                "studentName": student.user.name,
                "attendance": attendance_data
            }

            serializer = AttendanceListResponseSerializer(res)
            response_data = serializer.data

            # 조회 결과를 캐시에 저장 (5분 동안)
            cache.set(cache_key, response_data, timeout=300)

            send_success_slack(request, "출결 조회", start_time)
            return Response(response_data)

        except Exception as e:
            send_error_slack(request, "출결 조회", start_time, error=e)
            return Response({"error": str(e)}, status=500)

    def post(self, request, student_id):
        start_time = datetime.now()
        try:
            data = request.data
            student = get_object_or_404(Student, id=student_id)

            AttendanceSummary.objects.get_or_create(
                student=student,
                grade=data["grade"],
                year=data["year"],
                defaults={
                    "total_days": 0,
                    "remarks": "",
                    "home_teacher": data.get("homeTeacher", "")
                }
            )

            AttendanceRecord.objects.create(
                student=student,
                grade=data["grade"],
                year=data["year"],
                attendance_type=data["attendanceType"],
                reason_type=data["reasonType"],
                date=data["date"],
                reason=data.get("reason", "")
            )

            # 출결 정보가 변경되었으므로 해당 학생의 모든 캐시 키 삭제
            cache.delete_pattern(f"attendance:{student_id}:*")

            send_success_slack(request, "출결 등록", start_time)
            return Response({"message": "Attendance record added successfully"}, status=201)

        except Exception as e:
            send_error_slack(request, "출결 등록", start_time, error=e)
            return Response({"error": str(e)}, status=500)

    def delete(self, request, student_id):
        start_time = datetime.now()
        try:
            data = request.data
            student = get_object_or_404(Student, id=student_id)

            deleted, _ = AttendanceRecord.objects.filter(
                student=student,
                grade=data["grade"],
                year=data["year"],
                attendance_type=data["attendanceType"],
                reason_type=data["reasonType"],
                date=data["date"]
            ).delete()

            if deleted:
                # 삭제 후 해당 학생의 캐시 키 전부 삭제
                cache.delete_pattern(f"attendance:{student_id}:*")
                send_success_slack(request, "출결 삭제", start_time)
                return Response({"message": "Attendance record deleted successfully"}, status=200)
            else:
                send_error_slack(request, "출결 삭제", start_time, error=Exception("Record not found"))
                return Response({"message": "Attendance record not found"}, status=404)

        except Exception as e:
            send_error_slack(request, "출결 삭제", start_time, error=e)
            return Response({"error": str(e)}, status=500)
