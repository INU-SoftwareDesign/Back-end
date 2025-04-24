from rest_framework import generics
from .models import Teacher
from .serializers import (
    TeacherListSerializer,
    TeacherDetailSerializer,
    TeacherUpdateSerializer
)

class TeacherView(generics.ListAPIView):
    queryset = Teacher.objects.select_related('user').all()
    serializer_class = TeacherListSerializer

class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teacher.objects.select_related('user').all()

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return TeacherUpdateSerializer
        return TeacherDetailSerializer
