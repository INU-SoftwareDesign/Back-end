from rest_framework import generics, mixins, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Grade
from .serializers import GradeSerializer
from students.models import Student
from subjects.models import Subject

def calculate_total_average(student):
    grades = Grade.objects.filter(student=student)
    total = sum(g.score for g in grades)
    average = round(total / grades.count(), 2) if grades.exists() else 0
    return total, average

class GradeView(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    serializer_class = GradeSerializer

    def get_queryset(self):
        student_id = self.request.query_params.get('student_id')
        return Grade.objects.filter(student_id=student_id)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        student_id = request.query_params.get('student_id')
        student = get_object_or_404(Student, id=student_id)
        total, average = calculate_total_average(student)

        return Response({
            "student_id": student.id,
            "student_name": student.user.name,
            "grades": serializer.data,
            "total": total,
            "average": average
        })

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            student = get_object_or_404(Student, id=request.data['student_id'])
            subject = get_object_or_404(Subject, id=request.data['subject_id'])

            grade = Grade.objects.create(
                student=student,
                subject=subject,
                semester=serializer.validated_data['semester'],
                score=serializer.validated_data['score']
            )

            total, average = calculate_total_average(student)

            return Response({
                "grade": GradeSerializer(grade).data,
                "total": total,
                "average": average
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GradeDetailView(mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      generics.GenericAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    def patch(self, request, *args, **kwargs):
        grade = self.get_object()
        serializer = self.get_serializer(grade, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            total, average = calculate_total_average(grade.student)
            return Response({
                "grade": serializer.data,
                "total": total,
                "average": average
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        grade = self.get_object()
        student = grade.student
        grade.delete()

        total, average = calculate_total_average(student)

        return Response({
            "total": total,
            "average": average
        }, status=status.HTTP_200_OK)
