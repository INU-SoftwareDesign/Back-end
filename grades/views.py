from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import GradeGroup, Grade
from students.models import Student
from classrooms.models import Classroom
from .serializers import GradeStudentStatusSerializer, GradeInputSerializer
from django.shortcuts import get_object_or_404
from datetime import datetime

class GradeManagementStatusView(APIView):
    def get(self, request):
        grade = request.query_params.get("grade")
        class_ = request.query_params.get("class")
        semester = request.query_params.get("semester")

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
        return Response({
            "semesterPeriod": {
                "start": "2025-05-01",
                "end": "2025-05-07"
            },
            "students": serializer.data
        })

class GradeUpdateView(APIView):
    def post(self, request, student_id):
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
            return Response({"message": "Grades submitted successfully"}, status=200)
        return Response({"error": "Invalid subject format or missing fields"}, status=400)

    def patch(self, request, student_id):
        student = get_object_or_404(Student, id=student_id)
        serializer = GradeInputSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({"error": "Invalid input"}, status=400)
        
        data = serializer.validated_data
        grade_group = GradeGroup.objects.filter(student=student).order_by('-updated_at').first()
        if not grade_group:
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

        return Response({"message": "Grades patched successfully"}, status=200)

    def get_subject_id_by_name(self, name):
        from subjects.models import Subject
        subject = get_object_or_404(Subject, name=name)
        return subject.id

class GradeOverviewView(APIView):
    def get(self, request, student_id):
        grade = request.query_params.get("grade")
        semester = request.query_params.get("semester")

        student = get_object_or_404(Student, id=student_id)
        group_qs = GradeGroup.objects.filter(student=student)
        if grade:
            group_qs = group_qs.filter(grade=grade)
        if semester:
            group_qs = group_qs.filter(semester=semester)

        grade_group = group_qs.order_by('-updated_at').first()
        if not grade_group:
            return Response({"error": "성적 정보가 없습니다."}, status=404)

        grades = grade_group.grades.select_related('subject')

        total_students = Student.objects.filter(classroom=student.classroom).count()
        subject_results = []
        total_credits = 0
        weighted_total_score = 0
        weighted_grade_sum = 0

        for grade in grades:
            subject_name = grade.subject.name
            credits = grade.credits
            total_score = grade.total_score

            all_scores = list(Grade.objects.filter(
                grade_group__semester=grade_group.semester,
                grade_group__grade=grade_group.grade,
                subject=grade.subject
            ).values_list('total_score', flat=True))

            all_scores.sort(reverse=True)
            rank = sum(1 for s in all_scores if s > total_score) + 1
            percentile = rank / len(all_scores)

            if percentile <= 0.1:
                grade_level = 1
            elif percentile <= 0.3:
                grade_level = 2
            elif percentile <= 0.6:
                grade_level = 3
            else:
                grade_level = 4

            subject_results.append({
                "name": subject_name,
                "credits": credits,
                "midterm": grade.midterm,
                "final": grade.final,
                "performance": grade.performance,
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
        for g in GradeGroup.objects.filter(grade=grade_group.grade, semester=grade_group.semester):
            g_total = sum(gr.total_score * gr.credits for gr in g.grades.all())
            g_credits = sum(gr.credits for gr in g.grades.all())
            if g_credits > 0:
                all_totals.append(g_total / g_credits)

        all_totals.sort(reverse=True)
        my_rank = all_totals.index(sum_total_score) + 1

        return Response({
            "studentId": student.student_id,
            "studentName": student.user.name,
            "grade": student.classroom.grade if student.classroom else None,
            "class": student.classroom.class_number if student.classroom else None,
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
        })
