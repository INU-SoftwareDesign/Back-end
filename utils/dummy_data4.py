import random
from datetime import datetime
from django.utils import timezone
from faker import Faker

from accounts.models import User
from students.models import Student
from subjects.models import Subject
from classrooms.models import Classroom
from grades.models import GradeGroup, Grade

fake = Faker('ko_KR')

# 2학년 1반에 속한 모든 학생 조회
classroom = Classroom.objects.get(grade=2, class_number=1)
students = Student.objects.filter(classroom=classroom)

# 과목 기준: 전체 Subject 중 앞의 5개
subjects = list(Subject.objects.all())[:5]

# 2학년 1반 학생 중, 성적 정보가 없는 학생만 필터링
target_students = []
for student in students:
    if not GradeGroup.objects.filter(student=student).exists():
        target_students.append(student)

# 1학년 1학기, 1학년 2학기 성적 추가
for student in target_students:
    for grade_year, semester in [(1, '1학기'), (1, '2학기')]:
        group = GradeGroup.objects.create(
            student=student,
            grade=f'{grade_year}학년',
            semester=semester,
            grade_status='입력완료',
            updated_at=timezone.now()
        )
        for subject in subjects:
            # 같은 seed 방식을 유지해 동일한 재현성 확보
            random.seed(f"{student.id}-{grade_year}-{semester}-{subject.id}")
            mid = round(random.uniform(50, 100), 1)
            fin = round(random.uniform(50, 100), 1)
            perf = round(random.uniform(50, 100), 1)
            total = round((mid + fin + perf) / 3, 1)
            Grade.objects.create(
                grade_group=group,
                subject=subject,
                credits=3,
                midterm=mid,
                final=fin,
                performance=perf,
                total_score=total
            )

print("✅ dummy_data4.py 실행 완료: 2학년 1반 나머지 학생들에 대해 1학년 1·2학기 성적 추가 완료")
