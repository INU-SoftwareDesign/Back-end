from rest_framework import generics
from .models import Attendance
from .serializers import AttendanceSerializer

class AttendanceView(generics.ListCreateAPIView):
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        student_id = self.request.query_params.get('student_id')
        return Attendance.objects.filter(student_id=student_id).select_related('student__user')

class AttendanceDetailView(generics.RetrieveUpdateAPIView):
    queryset = Attendance.objects.select_related('student__user')
    serializer_class = AttendanceSerializer
