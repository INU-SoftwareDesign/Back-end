from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import AttendanceRecord, AttendanceSummary
from students.models import Student
from .serializers import AttendanceListResponseSerializer
from django.db.models import Q
from collections import defaultdict

class AttendanceView(APIView):
    def get(self, request, student_id):
        grade = request.GET.get("grade")
        year = request.GET.get("year")

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
        return Response(serializer.data)

    def post(self, request, student_id):
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
        return Response({"message": "Attendance record added successfully"}, status=201)

    def delete(self, request, student_id):
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

        return Response({"message": "Attendance record deleted successfully"}, status=200 if deleted else 404)
