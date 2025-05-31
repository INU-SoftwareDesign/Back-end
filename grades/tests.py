from django.test import SimpleTestCase
from django.urls import resolve
from grades.serializers import GradeStudentStatusSerializer, GradeInputSerializer
from grades.views import (
    GradeManagementStatusView,
    GradeOverviewView,
    GradeUpdateView,
    GradeInputPeriodView,
)


class GradeSerializerBasicTest(SimpleTestCase):
    def test_grade_student_status_serializer_fields(self):
        """
        GradeStudentStatusSerializer에 정의된 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = GradeStudentStatusSerializer()
        expected_fields = {
            "id",
            "name",
            "studentId",
            "grade",
            "classNumber",
            "number",
            "profileImage",
            "gradeStatus",
        }
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_grade_input_serializer_fields(self):
        """
        GradeInputSerializer에 정의된 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = GradeInputSerializer()
        expected_fields = {
            "grade",
            "semester",
            "gradeStatus",
            "updatedAt",
            "subjects",
        }
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)


class URLPatternsResolveTest(SimpleTestCase):
    def test_management_status_url_resolves(self):
        """
        '/api/grades/management-status' 경로가 GradeManagementStatusView로 연결되는지 확인합니다.
        """
        resolver = resolve("/api/grades/management-status")
        self.assertEqual(resolver.func.view_class, GradeManagementStatusView)

    def test_grade_overview_url_resolves(self):
        """
        '/api/grades/students/<student_id>/overview' 경로가 GradeOverviewView로 연결되는지 확인합니다.
        """
        resolver = resolve("/api/grades/students/123/overview")
        self.assertEqual(resolver.func.view_class, GradeOverviewView)

    def test_grade_update_url_resolves(self):
        """
        '/api/grades/students/<student_id>' 경로가 GradeUpdateView로 연결되는지 확인합니다.
        """
        resolver = resolve("/api/grades/students/123")
        self.assertEqual(resolver.func.view_class, GradeUpdateView)

    def test_grade_input_period_url_resolves(self):
        """
        '/api/grades/input-period' 경로가 GradeInputPeriodView로 연결되는지 확인합니다.
        """
        resolver = resolve("/api/grades/input-period")
        self.assertEqual(resolver.func.view_class, GradeInputPeriodView)
