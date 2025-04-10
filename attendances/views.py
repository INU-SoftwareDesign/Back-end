from rest_framework import generics, status
from rest_framework.response import Response
from .models import Attendance
from .serializers import AttendanceSerializer, AttendanceListSerializer
from students.models import Student
from django.shortcuts import get_object_or_404

class AttendanceView(generics.CreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def get(self, request):
        student_id = request.query_params.get('student_id')
        student = get_object_or_404(Student, id=student_id)
        attendances = Attendance.objects.filter(student=student).order_by('date')
        data = {
            "student_id": student.id,
            "student_name": student.user.name,
            "attendances": [
                {
                    "id": a.id,
                    "date": a.date,
                    "status": a.status,
                    "note": a.note
                }
                for a in attendances
            ]
        }
        return Response(data)

class AttendanceDetailView(generics.RetrieveUpdateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
