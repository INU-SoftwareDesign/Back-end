from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Student
from .serializers import StudentListSerializer, StudentDetailSerializer, StudentUpdateSerializer
from rest_framework.permissions import IsAuthenticated

class StudentListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentListSerializer

    def get_queryset(self):
        queryset = Student.objects.select_related('user', 'classroom').all()

        grade = self.request.query_params.get('grade')
        class_num = self.request.query_params.get('class')
        search = self.request.query_params.get('search')

        if grade:
            queryset = queryset.filter(classroom__grade=grade)
        if class_num:
            queryset = queryset.filter(classroom__class_number=class_num)
        if search:
            queryset = queryset.filter(user__name__icontains=search)

        return queryset


class StudentDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Student.objects.select_related('user', 'classroom').prefetch_related(
        'history', 'academic_records', 'parentstudent_set__parent__user'
    )
    serializer_class = StudentDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

    def update(self, request, *args, **kwargs):
        student = self.get_object()
        serializer = StudentUpdateSerializer(student, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Student information updated successfully"}, status=200)


    def destroy(self, request, *args, **kwargs):
        student = self.get_object()
        self.perform_destroy(student)
        return Response(status=204)