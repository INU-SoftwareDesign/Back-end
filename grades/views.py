# grades/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import GradeGroup, Grade
from students.models import Student
from classrooms.models import Classroom
from .serializers import GradeStudentStatusSerializer, GradeInputSerializer
from django.shortcuts import get_object_or_404
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from utils.slack import send_success_slack, send_error_slack
from datetime import datetime
from django.core.cache import cache  # ← 캐시 사용을 위해 import 추가


class GradeManagementStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_time = datetime.now()
        try:
            grade = request.query_params.get("grade")
            class_ = request.query_params.get("class")
            semester = request.query_params.get("semester")

            # 캐시 키 생성: grade, class_, semester 값 조합
            cache_key = f"grades:management_status:grade:{grade or 'all'}:class:{class_ or 'all'}:semester:{semester or 'all'}"
            cached_payload = cache.get(cache_key)
            if cached_payload is not None:
                return Response(cached_payload)

            students = Student.objects.all()
            if grade:
                students = students.filter(classroom__grade=grade)
            if class_:
                students = students.filter(classroom__class_number=class_)

            result = []
            for student in students:
                group_qs = GradeGroup.objects.filter(student=student)
                if semester:
                    group_qs = group_qs.filter(semester=semester)
                group = group_qs.order_by('-updated_at').first()
                student.gradeStatus = group.grade_status if group else '미입력'
                result.append(student)

            serializer = GradeStudentStatusSerializer(result, many=True)
            students_data = serializer.data

            payload = {
                "semesterPeriod": {
                    "start": "2025-05-01",
                    "end": "2025-06-16"
                },
                "students": students_data
            }
            # 조회 결과를 캐시에 저장 (5분 동안 유지)
            cache.set(cache_key, payload, timeout=300)

            send_success_slack(request, "성적 목록 조회", start_time)
            return Response(payload)
        except Exception as e:
            send_error_slack(request, "성적 목록 조회", start_time, error=e)
            return Response({"error": str(e)}, status=500)


class GradeUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, student_id):
        start_time = datetime.now()
        try:
            student = get_object_or_404(Student, id=student_id)
            serializer = GradeInputSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                group = GradeGroup.objects.create(
                    student=student,
                    grade=data['grade'],
                    semester=data['semester'],
                    grade_status=data['gradeStatus'],
                    updated_at=data['updatedAt']
                )
                for item in data['subjects']:
                    Grade.objects.create(
                        grade_group=group,
                        subject_id=self.get_subject_id_by_name(item['subject']),
                        credits=item['credits'],
                        midterm=item['midterm'],
                        final=item['final'],
                        performance=item['performance'],
                        total_score=item['totalScore']
                    )

                # 성적 등록 후 캐시 무효화:
                # - GradeManagementStatusView 캐시 전부 삭제
                cache.delete_pattern("grades:management_status:*")
                # - 해당 학생의 GradeOverviewView 캐시 삭제
                cache.delete_pattern(f"grades:overview:{student_id}:*")

                send_success_slack(request, "성적 등록", start_time)
                return Response({"message": "Grades submitted successfully"}, status=200)
            send_error_slack(request, "성적 등록", start_time, error=Exception("Invalid subject format or missing fields"))
            return Response({"error": "Invalid subject format or missing fields"}, status=400)
        except Exception as e:
            send_error_slack(request, "성적 등록", start_time, error=e)
            return Response({"error": str(e)}, status=500)

    def patch(self, request, student_id):
        start_time = datetime.now()
        try:
            student = get_object_or_404(Student, id=student_id)
            serializer = GradeInputSerializer(data=request.data, partial=True)
            if not serializer.is_valid():
                send_error_slack(request, "성적 수정", start_time, error=Exception("Invalid input"))
                return Response({"error": "Invalid input"}, status=400)

            data = serializer.validated_data
            grade_group = GradeGroup.objects.filter(student=student).order_by('-updated_at').first()
            if not grade_group:
                send_error_slack(request, "성적 수정", start_time, error=Exception("성적 정보가 없습니다."))
                return Response({"error": "성적 정보가 없습니다."}, status=404)

            if 'gradeStatus' in data:
                grade_group.grade_status = data['gradeStatus']
            if 'updatedAt' in data:
                grade_group.updated_at = data['updatedAt']
            grade_group.save()

            if 'subjects' in data:
                for item in data['subjects']:
                    subject_name = item.get('subject')
                    from subjects.models import Subject
                    subject = get_object_or_404(Subject, name=subject_name)

                    grade = Grade.objects.filter(grade_group=grade_group, subject=subject).first()
                    if not grade:
                        continue

                    grade.credits = item.get('credits', grade.credits)
                    grade.midterm = item.get('midterm', grade.midterm)
                    grade.final = item.get('final', grade.final)
                    grade.performance = item.get('performance', grade.performance)
                    grade.total_score = item.get('totalScore', grade.total_score)
                    grade.save()

            # 성적 수정 후 캐시 무효화:
            cache.delete_pattern("grades:management_status:*")
            cache.delete_pattern(f"grades:overview:{student_id}:*")

            send_success_slack(request, "성적 수정", start_time)
            return Response({"message": "Grades patched successfully"}, status=200)
        except Exception as e:
            send_error_slack(request, "성적 수정", start_time, error=e)
            return Response({"error": str(e)}, status=500)

    def get_subject_id_by_name(self, name):
        from subjects.models import Subject
        subject = get_object_or_404(Subject, name=name)
        return subject.id


class GradeOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        start_time = datetime.now()
        try:
            grade = request.query_params.get("grade")
            semester = request.query_params.get("semester")

            # 캐시 키 생성: 학생 ID + grade + semester
            cache_key = f"grades:overview:{student_id}:grade:{grade or 'all'}:semester:{semester or 'all'}"
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)

            student = get_object_or_404(Student, id=student_id)
            group_qs = GradeGroup.objects.filter(student=student)
            if grade:
                grade_val = f"{grade}학년" if '학년' not in grade else grade
                group_qs = group_qs.filter(grade=grade_val)
            if semester:
                semester_val = f"{semester}학기" if '학기' not in semester else semester
                group_qs = group_qs.filter(semester=semester_val)

            grade_group = group_qs.order_by('-updated_at').first()
            if not grade_group:
                send_error_slack(request, "성적 상세 조회", start_time, error=Exception("성적 정보가 없습니다."))
                return Response({"error": "성적 정보가 없습니다."}, status=404)

            grades = grade_group.grades.select_related('subject')
            subject_results = []
            total_credits = 0
            weighted_total_score = 0
            weighted_grade_sum = 0

            for grade_obj in grades:
                subject_name = grade_obj.subject.name
                credits = grade_obj.credits
                total_score = grade_obj.total_score

                all_scores = list(Grade.objects.filter(
                    grade_group__semester=grade_group.semester,
                    grade_group__grade=grade_group.grade,
                    subject=grade_obj.subject
                ).values_list('total_score', flat=True))

                all_scores.sort(reverse=True)
                rank = sum(1 for s in all_scores if s > total_score) + 1
                percentile = rank / len(all_scores)

                if percentile <= 0.04:
                    grade_level = 1
                elif percentile <= 0.11:
                    grade_level = 2
                elif percentile <= 0.23:
                    grade_level = 3
                elif percentile <= 0.40:
                    grade_level = 4
                elif percentile <= 0.60:
                    grade_level = 5
                elif percentile <= 0.77:
                    grade_level = 6
                elif percentile <= 0.89:
                    grade_level = 7
                elif percentile <= 0.96:
                    grade_level = 8
                else:
                    grade_level = 9

                subject_results.append({
                    "name": subject_name,
                    "credits": credits,
                    "midterm": grade_obj.midterm,
                    "final": grade_obj.final,
                    "performance": grade_obj.performance,
                    "totalScore": total_score,
                    "rank": f"{rank}/{len(all_scores)}",
                    "gradeLevel": grade_level
                })

                total_credits += credits
                weighted_total_score += total_score * credits
                weighted_grade_sum += grade_level * credits

            sum_midterm = sum([g.midterm for g in grades]) / len(grades)
            sum_final = sum([g.final for g in grades]) / len(grades)
            sum_performance = sum([g.performance for g in grades]) / len(grades)
            sum_total_score = weighted_total_score / total_credits
            converted_grade = round(weighted_grade_sum / total_credits, 2)

            all_totals = []
            same_grade_students = Student.objects.filter(classroom__grade=student.classroom.grade)
            for s in same_grade_students:
                ggroup = GradeGroup.objects.filter(student=s, semester=grade_group.semester, grade=grade_group.grade).order_by('-updated_at').first()
                if not ggroup:
                    continue
                ggrades = ggroup.grades.all()
                g_total = sum(gr.total_score * gr.credits for gr in ggrades)
                g_credits = sum(gr.credits for gr in ggrades)
                if g_credits > 0:
                    all_totals.append(g_total / g_credits)

            all_totals.sort(reverse=True)
            my_rank = next((i + 1 for i, score in enumerate(all_totals) if abs(score - sum_total_score) < 1e-6), None)
            if my_rank is None:
                send_error_slack(request, "성적 상세 조회", start_time, error=Exception("등수를 계산할 수 없습니다."))
                return Response({"error": "등수를 계산할 수 없습니다."}, status=500)

            payload = {
                "studentId": student.student_id,
                "studentName": student.user.name,
                "grade": student.classroom.grade if student.classroom else None,
                "classNumber": student.classroom.class_number if student.classroom else None,
                "number": student.student_number,
                "subjects": subject_results,
                "totals": {
                    "totalCredits": total_credits,
                    "sumMidterm": round(sum_midterm, 1),
                    "sumFinal": round(sum_final, 1),
                    "sumPerformance": round(sum_performance, 1),
                    "sumTotalScore": round(sum_total_score, 1)
                },
                "finalSummary": {
                    "totalStudents": len(all_totals),
                    "finalRank": f"{my_rank}/{len(all_totals)}",
                    "finalConvertedGrade": converted_grade
                },
                "radarChart": {
                    "labels": [s["name"] for s in subject_results],
                    "data": [s["totalScore"] for s in subject_results]
                }
            }

            # 조회 결과를 캐시에 저장 (5분 동안 유지)
            cache.set(cache_key, payload, timeout=300)

            send_success_slack(request, "성적 상세 조회", start_time)
            return Response(payload)
        except Exception as e:
            send_error_slack(request, "성적 상세 조회", start_time, error=e)
            return Response({"error": str(e)}, status=500)


class GradeInputPeriodView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "semesterPeriod": {
                "start": "2025-05-01",
                "end": "2025-06-16"
            }
        })
