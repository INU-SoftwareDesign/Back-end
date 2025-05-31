from django.test import SimpleTestCase
from django.urls import resolve
from consultations.serializers import (
    CounselingSerializer,
    TeacherCounselingRequestSerializer,
    CounselingRequestSerializer,
    CounselingApproveSerializer,
    CounselingUpdateSerializer,
)
from consultations.views import (
    StudentCounselingListView,
    TeacherCounselingRequestListView,
    TeacherScheduledCounselingListView,
    TeacherCounselingCalendarView,
    AvailableCounselingTimesView,
    CounselingRequestCreateView,
    CounselingApproveView,
    CounselingUpdateCancelView,
)


class CounselingSerializerBasicTest(SimpleTestCase):
    def test_counseling_serializer_fields(self):
        """
        CounselingSerializer에 정의된 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = CounselingSerializer()
        expected_fields = {
            'id',
            'studentId',
            'studentName',
            'grade',
            'classNumber',
            'number',
            'requestDate',
            'counselingDate',
            'counselingTime',
            'counselorName',
            'counselingType',
            'counselingCategory',
            'status',
            'location',
            'requestContent',
            'resultContent',
            'contactNumber',
        }
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_teacher_counseling_request_serializer_fields(self):
        """
        TeacherCounselingRequestSerializer의 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = TeacherCounselingRequestSerializer()
        expected_fields = {
            'id',
            'studentId',
            'studentName',
            'grade',
            'classNumber',
            'number',
            'requestDate',
            'counselingDate',
            'counselingTime',
            'counselingType',
            'counselingCategory',
            'status',
            'requestContent',
            'contactNumber',
        }
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_counseling_request_serializer_fields(self):
        """
        CounselingRequestSerializer의 입력(write-only) 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = CounselingRequestSerializer()
        expected_fields = {
            'studentId',
            'teacherId',
            'counselingDate',
            'counselingTime',
            'counselingType',
            'counselingCategory',
            'requestContent',
            'contactNumber',
        }
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_counseling_approve_serializer_fields(self):
        """
        CounselingApproveSerializer의 필드가 올바르게 설정되었는지 확인합니다.
        """
        serializer = CounselingApproveSerializer()
        expected_fields = {'location'}
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_counseling_update_serializer_fields(self):
        """
        CounselingUpdateSerializer의 필드들이 올바르게 설정되었는지 확인합니다.
        """
        serializer = CounselingUpdateSerializer()
        expected_fields = {
            'counselingDate',
            'counselingTime',
            'location',
            'status',
            'resultContent',
            'requestContent',
        }
        actual_fields = set(serializer.fields.keys())
        self.assertEqual(actual_fields, expected_fields)


class URLPatternsResolveTest(SimpleTestCase):
    def test_student_counseling_list_url_resolves(self):
        """
        '/api/counselings/student/<student_id>' 경로가 StudentCounselingListView로 연결되는지 확인합니다.
        """
        resolver = resolve('/api/counselings/student/123')
        self.assertEqual(resolver.func.view_class, StudentCounselingListView)

    def test_teacher_counseling_request_list_url_resolves(self):
        """
        '/api/counselings/teacher/<teacher_id>/requests' 경로가 TeacherCounselingRequestListView로 연결되는지 확인합니다.
        """
        resolver = resolve('/api/counselings/teacher/45/requests')
        self.assertEqual(resolver.func.view_class, TeacherCounselingRequestListView)

    def test_teacher_scheduled_counseling_list_url_resolves(self):
        """
        '/api/counselings/teacher/<teacher_id>/scheduled' 경로가 TeacherScheduledCounselingListView로 연결되는지 확인합니다.
        """
        resolver = resolve('/api/counselings/teacher/45/scheduled')
        self.assertEqual(resolver.func.view_class, TeacherScheduledCounselingListView)

    def test_teacher_counseling_calendar_url_resolves(self):
        """
        '/api/counselings/teacher/<teacher_id>/calendar' 경로가 TeacherCounselingCalendarView로 연결되는지 확인합니다.
        """
        resolver = resolve('/api/counselings/teacher/45/calendar')
        self.assertEqual(resolver.func.view_class, TeacherCounselingCalendarView)

    def test_available_counseling_times_url_resolves(self):
        """
        '/api/counselings/available-times' 경로가 AvailableCounselingTimesView로 연결되는지 확인합니다.
        """
        resolver = resolve('/api/counselings/available-times')
        self.assertEqual(resolver.func.view_class, AvailableCounselingTimesView)

    def test_counseling_request_create_url_resolves(self):
        """
        '/api/counselings/request' 경로가 CounselingRequestCreateView로 연결되는지 확인합니다.
        """
        resolver = resolve('/api/counselings/request')
        self.assertEqual(resolver.func.view_class, CounselingRequestCreateView)

    def test_counseling_approve_url_resolves(self):
        """
        '/api/counselings/<counseling_id>/approve' 경로가 CounselingApproveView로 연결되는지 확인합니다.
        """
        resolver = resolve('/api/counselings/77/approve')
        self.assertEqual(resolver.func.view_class, CounselingApproveView)

    def test_counseling_update_cancel_url_resolves(self):
        """
        '/api/counselings/<counseling_id>' 경로가 CounselingUpdateCancelView로 연결되는지 확인합니다.
        """
        resolver = resolve('/api/counselings/77')
        self.assertEqual(resolver.func.view_class, CounselingUpdateCancelView)
