# attendances/tests.py

from django.test import SimpleTestCase
from django.urls import resolve
from attendances.views import AttendanceView
from attendances.serializers import AttendanceListResponseSerializer, AttendanceResponseSerializer


class AttendanceSerializerBasicTest(SimpleTestCase):
    def test_attendance_list_response_serializer_fields(self):
        """
        AttendanceListResponseSerializer가 정의한 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = AttendanceListResponseSerializer()
        expected_fields = {"studentId", "studentName", "attendance"}
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_attendance_response_serializer_fields(self):
        """
        AttendanceResponseSerializer가 정의한 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = AttendanceResponseSerializer()
        expected_fields = {
            "grade",
            "year",
            "homeTeacher",
            "totalDays",
            "remarks",
            "attendance",
            "details",
        }
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)


class URLPatternsResolveTest(SimpleTestCase):
    def test_attendance_manage_url_resolves(self):
        """
        '/api/attendances/students/<student_id>' 경로가 AttendanceView로 연결되는지 확인합니다.
        """
        resolver = resolve("/api/attendances/students/123")
        self.assertEqual(resolver.func.view_class, AttendanceView)
