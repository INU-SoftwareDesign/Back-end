from rest_framework import generics
from .models import Student
from .serializers import StudentListSerializer, StudentDetailSerializer

class StudentView(generics.ListAPIView):
    queryset = Student.objects.select_related('user', 'classroom').all()
    serializer_class = StudentListSerializer

class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.select_related('user', 'classroom').all()
    serializer_class = StudentDetailSerializer
