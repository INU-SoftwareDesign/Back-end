# students/views.py

from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Student
from .serializers import StudentListSerializer, StudentDetailSerializer, StudentUpdateSerializer
from rest_framework.permissions import IsAuthenticated
from utils.slack import send_success_slack, send_error_slack
from datetime import datetime
from django.core.cache import cache  # ← 캐시 사용을 위해 import 추가


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

    def list(self, request, *args, **kwargs):
        start_time = datetime.now()
        try:
            grade = request.query_params.get('grade') or 'all'
            class_num = request.query_params.get('class') or 'all'
            search = request.query_params.get('search') or 'all'

            cache_key = f"students:list:grade:{grade}:class:{class_num}:search:{search}"
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                send_success_slack(request, "학생 목록 조회 (캐시)", start_time)
                return Response(cached_data)

            response = super().list(request, *args, **kwargs)
            data = response.data

            cache.set(cache_key, data, timeout=300)  # 5분간 캐시
            send_success_slack(request, "학생 목록 조회", start_time)
            return response
        except Exception as e:
            send_error_slack(request, "학생 목록 조회", start_time, error=e)
            return Response({"error": str(e)}, status=500)


class StudentDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Student.objects.select_related('user', 'classroom').prefetch_related(
        'history', 'academic_records', 'parentstudent_set__parent__user'
    )
    serializer_class = StudentDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        start_time = datetime.now()
        student_id = kwargs.get('pk')
        cache_key = f"students:detail:{student_id}"
        try:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                send_success_slack(request, "학생 상세 조회 (캐시)", start_time)
                return Response(cached_data)

            response = super().retrieve(request, *args, **kwargs)
            data = response.data

            cache.set(cache_key, data, timeout=300)  # 5분간 캐시
            send_success_slack(request, "학생 상세 조회", start_time)
            return response
        except Student.DoesNotExist as e:
            send_error_slack(request, "학생 상세 조회", start_time, error=e)
            return Response({"error": "Student not found"}, status=404)
        except Exception as e:
            send_error_slack(request, "학생 상세 조회", start_time, error=e)
            return Response({"error": str(e)}, status=500)

    def update(self, request, *args, **kwargs):
        start_time = datetime.now()
        try:
            student = self.get_object()
            response = super().update(request, *args, **kwargs)

            # 캐시 무효화: 상세 조회와 목록 조회
            cache.delete(f"students:detail:{student.id}")
            cache.delete_pattern("students:list:*")

            send_success_slack(request, "학생 정보 수정", start_time)
            return Response({"message": "Student information updated successfully"}, status=200)
        except Exception as e:
            send_error_slack(request, "학생 정보 수정", start_time, error=e)
            return Response({"error": str(e)}, status=500)

    def destroy(self, request, *args, **kwargs):
        student = self.get_object()
        student_id = student.id
        self.perform_destroy(student)

        # 캐시 무효화: 상세 조회와 목록 조회
        cache.delete(f"students:detail:{student_id}")
        cache.delete_pattern("students:list:*")

        return Response(status=204)
