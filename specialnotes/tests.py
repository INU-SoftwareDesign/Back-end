from django.test import SimpleTestCase
from django.urls import resolve
from specialnotes.serializers import (
    CareerAspirationSerializer,
    SpecialNoteSerializer,
    SpecialNoteCreateSerializer,
    SpecialNoteUpdateSerializer,
)
from specialnotes.views import (
    StudentSpecialNoteListView,
    SpecialNoteCreateView,
    SpecialNoteDetailView,
)


class SpecialNoteSerializerBasicTest(SimpleTestCase):
    def test_career_aspiration_serializer_fields(self):
        """
        CareerAspirationSerializer에 정의된 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = CareerAspirationSerializer()
        expected_fields = {"student", "parent"}
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_special_note_serializer_fields(self):
        """
        SpecialNoteSerializer에 정의된 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = SpecialNoteSerializer()
        expected_fields = {
            "id",
            "studentId",
            "grade",
            "classNumber",
            "teacherId",
            "teacherName",
            "specialTalent",
            "careerAspiration",
            "note",
            "createdAt",
            "updatedAt",
        }
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_special_note_create_serializer_fields(self):
        """
        SpecialNoteCreateSerializer에 정의된 입력 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = SpecialNoteCreateSerializer()
        expected_fields = {
            "studentId",
            "grade",
            "classNumber",
            "teacherId",
            "teacherName",
            "specialTalent",
            "careerAspiration",
            "note",
        }
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_special_note_update_serializer_fields(self):
        """
        SpecialNoteUpdateSerializer에 정의된 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = SpecialNoteUpdateSerializer()
        expected_fields = {"specialTalent", "careerAspiration", "note"}
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)


class URLPatternsResolveTest(SimpleTestCase):
    def test_student_special_note_list_url_resolves(self):
        """
        '/api/specialnotes/students/<student_id>' 경로가 StudentSpecialNoteListView로 연결되는지 확인합니다.
        """
        resolver = resolve("/api/specialnotes/students/20250001")
        self.assertEqual(resolver.func.view_class, StudentSpecialNoteListView)

    def test_special_note_create_url_resolves(self):
        """
        '/api/specialnotes/' 경로가 SpecialNoteCreateView로 연결되는지 확인합니다.
        """
        resolver = resolve("/api/specialnotes/")
        self.assertEqual(resolver.func.view_class, SpecialNoteCreateView)

    def test_special_note_detail_url_resolves(self):
        """
        '/api/specialnotes/<note_id>' 경로가 SpecialNoteDetailView로 연결되는지 확인합니다.
        """
        resolver = resolve("/api/specialnotes/77")
        self.assertEqual(resolver.func.view_class, SpecialNoteDetailView)
