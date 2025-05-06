from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Counseling
from .serializers import CounselingSerializer, CounselingRequestSerializer, CounselingApproveSerializer, CounselingUpdateSerializer, TeacherCounselingRequestSerializer, TeacherScheduledCounselingSerializer
from students.models import Student
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from teachers.models import Teacher
from utils.slack import send_success_slack, send_error_slack
from datetime import datetime

class StudentCounselingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        start_time = datetime.now()
        try:
            status_param = request.query_params.get('status')
            start_date = request.query_params.get('startDate')
            end_date = request.query_params.get('endDate')

            student = Student.objects.get(id=student_id)
            queryset = Counseling.objects.filter(student=student)

            if status_param:
                queryset = queryset.filter(status=status_param)
            if start_date:
                queryset = queryset.filter(counseling_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(counseling_date__lte=end_date)

            serializer = CounselingSerializer(queryset, many=True)
            send_success_slack(request, "학생 상담 내역 조회", start_time)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            send_error_slack(request, "학생 상담 내역 조회", start_time)
            return Response({"detail": "해당 학생이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
    
class TeacherCounselingRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, teacher_id):
        start_time = datetime.now()
        try:
            status_param = request.query_params.get('status')
            start_date = request.query_params.get('startDate')
            end_date = request.query_params.get('endDate')

            teacher = Teacher.objects.get(id=teacher_id)
            queryset = Counseling.objects.filter(teacher=teacher)

            if status_param:
                queryset = queryset.filter(status=status_param)
            else:
                queryset = queryset.filter(status='신청')

            if start_date:
                queryset = queryset.filter(counseling_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(counseling_date__lte=end_date)

            queryset = queryset.order_by('counseling_date', 'counseling_time')

            serializer = TeacherCounselingRequestSerializer(queryset, many=True)
            send_success_slack(request, "상담 신청 조회", start_time)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            send_error_slack(request, "상담 신청 조회", start_time)
            return Response({"detail": "해당 교사가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)


class TeacherScheduledCounselingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, teacher_id):
        start_time = datetime.now()
        try:
            status_list = ['예약확정']
            start_date = request.query_params.get('startDate')
            end_date = request.query_params.get('endDate')

            teacher = Teacher.objects.get(id=teacher_id)
            queryset = Counseling.objects.filter(teacher=teacher, status__in=status_list)

            if start_date:
                queryset = queryset.filter(counseling_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(counseling_date__lte=end_date)

            queryset = queryset.order_by('counseling_date', 'counseling_time')

            serializer = TeacherScheduledCounselingSerializer(queryset, many=True)
            send_success_slack(request, "확정 상담 일정 조회", start_time)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            send_error_slack(request, "확정 상담 일정 조회", start_time)
            return Response({"detail": "해당 교사가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

class TeacherCounselingCalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, teacher_id):
        start_time = datetime.now()
        try:
            year = request.query_params.get('year')
            month = request.query_params.get('month')

            if not year or not month:
                return Response({
                    "success": False,
                    "error": {
                        "code": "INVALID_PARAMS",
                        "message": "year와 month는 필수입니다."
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

            teacher = Teacher.objects.get(id=teacher_id)
            queryset = Counseling.objects.filter(
                teacher=teacher,
                status='예약확정',
                counseling_date__year=year,
                counseling_date__month=month
            )

            available_times = [
                "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
                "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
                "16:00", "16:30", "17:00"
            ]

            booked_slots = {}
            counselings_data = []

            for c in queryset:
                date_str = c.counseling_date.strftime('%Y-%m-%d')
                time_str = c.counseling_time.strftime('%H:%M')
                booked_slots.setdefault(date_str, []).append(time_str)

                counselings_data.append({
                    "id": c.id,
                    "studentName": c.student.user.name,
                    "counselingDate": date_str,
                    "counselingTime": time_str,
                    "status": c.status
                })

            send_success_slack(request, "상담 스케줄 조회", start_time)
            return Response({
                "success": True,
                "data": {
                    "availableTimes": available_times,
                    "bookedSlots": booked_slots,
                    "counselings": counselings_data
                }
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            send_error_slack(request, "상담 스케줄 조회", start_time)
            return Response({"detail": "해당 교사가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)


class AvailableCounselingTimesView(APIView):
    def get(self, request):
        start_time = datetime.now()
        teacher_id = request.query_params.get('teacherId')
        date_str = request.query_params.get('date')

        if not teacher_id or not date_str:
            return Response({
                "success": False,
                "error": "teacherId와 date는 필수입니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            teacher = Teacher.objects.get(id=teacher_id)
        except Teacher.DoesNotExist:
            return Response({
                "success": False,
                "error": "해당 교사가 존재하지 않습니다."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({
                "success": False,
                "error": "날짜 형식은 YYYY-MM-DD이어야 합니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        all_times = [
            "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
            "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
            "16:00", "16:30", "17:00"
        ]

        booked_qs = Counseling.objects.filter(
            teacher=teacher,
            counseling_date=date,
            status='예약확정'
        ).values_list('counseling_time', flat=True)

        booked_times = sorted(time.strftime('%H:%M') for time in booked_qs)
        available_times = [t for t in all_times if t not in booked_times]

        send_success_slack(request, "예약 가능 시간 조회", start_time)
        return Response({
            "success": True,
            "data": {
                "availableTimes": available_times,
                "bookedTimes": booked_times
            }
        }, status=status.HTTP_200_OK)


class CounselingRequestCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        start_time = datetime.now()
        serializer = CounselingRequestSerializer(data=request.data)
        if serializer.is_valid():
            counseling = serializer.save()
            send_success_slack(request, "상담 신청 등록", start_time)
            return Response({
                "success": True,
                "data": {
                    "id": counseling.id,
                    "status": counseling.status,
                    "requestDate": counseling.request_date,
                    "message": "상담 신청이 완료되었습니다."
                }
            }, status=status.HTTP_201_CREATED)
        send_error_slack(request, "상담 신청 등록", start_time)
        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class CounselingApproveView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, counseling_id):
        start_time = datetime.now()
        try:
            counseling = Counseling.objects.get(id=counseling_id)
        except Counseling.DoesNotExist:
            send_error_slack(request, "상담 신청 승인", start_time)
            return Response({"detail": "상담이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CounselingApproveSerializer(counseling, data=request.data, partial=True)
        if serializer.is_valid():
            counseling = serializer.save()
            send_success_slack(request, "상담 신청 승인", start_time)
            return Response({
                "success": True,
                "data": {
                    "id": counseling.id,
                    "status": counseling.status,
                    "location": counseling.location,
                    "message": "상담 신청이 승인되었습니다."
                }
            })
        
        send_error_slack(request, "상담 신청 승인", start_time)
        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class CounselingUpdateCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, counseling_id):
        start_time = datetime.now()
        try:
            counseling = Counseling.objects.get(id=counseling_id)
        except Counseling.DoesNotExist:
            send_error_slack(request, "상담 정보 수정", start_time)
            return Response({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "해당 상담이 존재하지 않습니다."
                }
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CounselingUpdateSerializer(counseling, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            send_success_slack(request, "상담 정보 수정", start_time)
            return Response({
                "success": True,
                "data": {
                    "id": counseling.id,
                    "message": "상담 정보가 수정되었습니다."
                }
            }, status=status.HTTP_200_OK)
        else:
            send_error_slack(request, "상담 정보 수정", start_time)
            return Response({
                "success": False,
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, counseling_id):
        start_time = datetime.now()
        try:
            counseling = Counseling.objects.get(id=counseling_id)
        except Counseling.DoesNotExist:
            send_error_slack(request, "상담 예약 취소", start_time)
            return Response({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "해당 상담이 존재하지 않습니다."
                }
            }, status=status.HTTP_404_NOT_FOUND)

        if counseling.status == '완료':
            send_error_slack(request, "상담 예약 취소", start_time)
            return Response({
                "success": False,
                "error": {
                    "code": "CANNOT_CANCEL_COMPLETED",
                    "message": "이미 완료된 상담은 취소할 수 없습니다."
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        counseling.delete()
        send_success_slack(request, "상담 예약 취소", start_time)
        return Response({
            "success": True,
            "data": {
                "message": "상담 예약이 취소되었습니다."
            }
        }, status=status.HTTP_200_OK)
