from django.test import SimpleTestCase
from django.urls import resolve
from students.serializers import (
    StudentListSerializer,
    StudentClassHistorySerializer,
    StudentDetailSerializer,
    StudentClassHistoryWriteSerializer,
    StudentAcademicRecordWriteSerializer,
    StudentUpdateSerializer,
)
from students.views import StudentListView, StudentDetailView


class StudentSerializerBasicTest(SimpleTestCase):
    def test_student_list_serializer_fields(self):
        """
        StudentListSerializer에 정의된 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = StudentListSerializer()
        expected_fields = {
            "id",
            "name",
            "studentId",
            "grade",
            "classNumber",
            "number",
            "recentCounselingDate",
            "profileImage",
        }
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_student_class_history_serializer_fields(self):
        """
        StudentClassHistorySerializer에 정의된 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = StudentClassHistorySerializer()
        expected_fields = {
            "grade",
            "classNumber",
            "number",
            "homeroom_teacher",
        }
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_student_detail_serializer_fields(self):
        """
        StudentDetailSerializer에 정의된 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = StudentDetailSerializer()
        expected_fields = {
            "profileImage",
            "name",
            "studentId",
            "grade",
            "classNumber",
            "number",
            "birthDate",
            "address",
            "fatherName",
            "motherName",
            "history",
            "academicRecords",
        }
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_student_class_history_write_serializer_fields(self):
        """
        StudentClassHistoryWriteSerializer에 정의된 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = StudentClassHistoryWriteSerializer()
        expected_fields = {
            "grade",
            "class_number",
            "number",
            "homeroom_teacher",
        }
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_student_academic_record_write_serializer_fields(self):
        """
        StudentAcademicRecordWriteSerializer에 정의된 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = StudentAcademicRecordWriteSerializer()
        expected_fields = {"description"}
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_student_update_serializer_fields(self):
        """
        StudentUpdateSerializer에 정의된 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = StudentUpdateSerializer()
        expected_fields = {
            "student_id",
            "student_number",
            "classroom",
            "profile_image",
            "history",
            "academicRecords",
        }
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)


class URLPatternsResolveTest(SimpleTestCase):
    def test_student_list_url_resolves(self):
        """
        '/api/students/' 경로가 StudentListView로 연결되는지 확인합니다.
        """
        resolver = resolve("/api/students/")
        self.assertEqual(resolver.func.view_class, StudentListView)

    def test_student_detail_url_resolves(self):
        """
        '/api/students/<pk>' 경로가 StudentDetailView로 연결되는지 확인합니다.
        """
        resolver = resolve("/api/students/123")
        self.assertEqual(resolver.func.view_class, StudentDetailView)
