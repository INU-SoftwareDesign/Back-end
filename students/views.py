from django.shortcuts import render
from rest_framework import generics
from .models import Student
from .serializers import StudentListSerializer, StudentDetailSerializer
from rest_framework.permissions import IsAuthenticated

# Create your views here.

class StudentView(generics.ListAPIView):
    queryset = Student.objects.select_related('user', 'classroom').all()
    serializer_class = StudentListSerializer
    #permission_classes = [IsAuthenticated]

class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.select_related('user', 'classroom').all()
    serializer_class = StudentDetailSerializer
    #permission_classes = [IsAuthenticated]