from django.test import SimpleTestCase
from django.urls import resolve
from feedbacks.serializers import (
    FeedbackNestedSerializer,
    FeedbackGroupSerializer,
    FeedbackCreateNestedSerializer,
    CreateFeedbackSerializer,
)
from feedbacks.views import (
    StudentFeedbackListView,
    FeedbackCreateView,
    FeedbackDetailView,
)


class FeedbackSerializerBasicTest(SimpleTestCase):
    def test_feedback_nested_serializer_fields(self):
        """
        FeedbackNestedSerializer에 정의된 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = FeedbackNestedSerializer()
        expected_fields = {"id", "category", "content"}
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_feedback_group_serializer_fields(self):
        """
        FeedbackGroupSerializer에 정의된 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = FeedbackGroupSerializer()
        expected_fields = {
            "id",
            "studentId",
            "grade",
            "classNumber",
            "teacherId",
            "teacherName",
            "createdAt",
            "updatedAt",
            "feedbacks",
        }
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_feedback_create_nested_serializer_fields(self):
        """
        FeedbackCreateNestedSerializer에 정의된 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = FeedbackCreateNestedSerializer()
        expected_fields = {"category", "content"}
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_create_feedback_serializer_fields(self):
        """
        CreateFeedbackSerializer에 정의된 입력 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = CreateFeedbackSerializer()
        expected_fields = {
            "studentId",
            "grade",
            "classNumber",
            "teacherId",
            "teacherName",
            "feedbacks",
        }
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)


class URLPatternsResolveTest(SimpleTestCase):
    def test_student_feedback_list_url_resolves(self):
        """
        '/api/feedbacks/students/<student_id>' 경로가 StudentFeedbackListView로 연결되는지 확인합니다.
        """
        resolver = resolve("/api/feedbacks/students/20250001")
        self.assertEqual(resolver.func.view_class, StudentFeedbackListView)

    def test_feedback_create_url_resolves(self):
        """
        '/api/feedbacks/' 경로가 FeedbackCreateView로 연결되는지 확인합니다.
        """
        resolver = resolve("/api/feedbacks/")
        self.assertEqual(resolver.func.view_class, FeedbackCreateView)

    def test_feedback_detail_url_resolves(self):
        """
        '/api/feedbacks/<feedback_id>' 경로가 FeedbackDetailView로 연결되는지 확인합니다.
        """
        resolver = resolve("/api/feedbacks/77")
        self.assertEqual(resolver.func.view_class, FeedbackDetailView)
