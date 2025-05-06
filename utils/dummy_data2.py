import random
from datetime import datetime, time
from django.utils import timezone
from faker import Faker

from accounts.models import User
from students.models import Student
from teachers.models import Teacher
from subjects.models import Subject
from classrooms.models import Classroom
from grades.models import GradeGroup, Grade
from attendances.models import AttendanceRecord, AttendanceSummary
from consultations.models import Counseling
from parents.models import Parent, ParentStudent

fake = Faker('ko_KR')
TODAY = datetime(2025, 5, 6)

classroom = Classroom.objects.get(grade=2, class_number=1)
teacher = classroom.teacher
students = Student.objects.filter(classroom=classroom)[:10]
subjects = list(Subject.objects.all())[:5]

# 학부모 연결
for idx, student in enumerate(students):
    parent_user = User.objects.create_user(
        username=f'parent_dummy_{idx+1}',
        password='pass1234',
        role='parent',
        name=fake.name(),
        phone=fake.phone_number(),
        birth_date=fake.date_of_birth(minimum_age=40, maximum_age=50),
        address=fake.address(),
        is_active=True,
        approval_status='approved'
    )
    parent = Parent.objects.create(user=parent_user)
    ParentStudent.objects.get_or_create(
        parent=parent,
        student=student,
        defaults={'role': random.choice(['father', 'mother'])}
    )

# 성적 입력
for student in students:
    for grade_year, semester in [(1, '1학기'), (1, '2학기'), (2, '1학기')]:
        group = GradeGroup.objects.create(
            student=student,
            grade=f'{grade_year}학년',
            semester=semester,
            grade_status='입력완료',
            updated_at=timezone.now()
        )
        for subject in subjects:
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

# 출결 입력 (한글 reason, remarks="")
REASON_TEXT = {
    "illness": ["감기로 인한 결석", "병원 진료", "복통으로 병원 방문"],
    "unauthorized": ["사유 없이 결석", "무단 지각"],
    "etc": ["가족 행사", "개인 사정", "교통 지연"]
}
ATTENDANCE_CHOICES = ['absence', 'lateness', 'earlyLeave']
REASON_CHOICES = ['illness', 'unauthorized', 'etc']

for student in students:
    for _ in range(5):
        att_type = random.choice(ATTENDANCE_CHOICES)
        reason_type = random.choice(REASON_CHOICES)
        AttendanceRecord.objects.create(
            student=student,
            grade='1',
            year=2024,
            date=fake.date_between_dates(datetime(2024, 3, 1), datetime(2025, 2, 28)),
            attendance_type=att_type,
            reason_type=reason_type,
            reason=random.choice(REASON_TEXT[reason_type])
        )

    AttendanceSummary.objects.get_or_create(
        student=student,
        grade='1',
        year=2024,
        defaults={
            'home_teacher': classroom.teacher.user.name,
            'total_days': 190,
            'remarks': ''
        }
    )

# 상담 요청/결과 텍스트
REQ_TEXT = [
    "중간고사 결과에 대한 피드백을 받고 싶습니다.",
    "학습 습관에 대한 조언을 구하고 싶습니다.",
    "진로 상담을 원합니다."
]
RES_TEXT = [
    "학습 계획 수립 및 자기주도학습 방법에 대해 논의함. 주 2회 학습 일지 작성 권고.",
    "성적 분석을 통해 부족한 과목 파악 후 보충 수업 추천.",
    "진로 탐색 활동 자료 제공 및 추후 심화 상담 예정."
]

# 학생 → 교사 상담
for student in students:
    Counseling.objects.create(
        student=student,
        teacher=teacher,
        counseling_date=datetime(2025, 5, random.randint(8, 10)),
        counseling_time=time(random.randint(9, 17), random.choice([0, 30])),
        counseling_type='교수상담',
        counseling_category=random.choice(['학업', '진로', '심리']),
        status=random.choice(['신청', '예약확정']),
        location='상담실 A',
        request_content=random.choice(REQ_TEXT),
        result_content='',
        contact_number=student.user.phone
    )

    for _ in range(random.randint(1, 2)):
        Counseling.objects.create(
            student=student,
            teacher=teacher,
            counseling_date=fake.date_between_dates(datetime(2025, 3, 1), TODAY),
            counseling_time=time(random.randint(9, 17), random.choice([0, 30])),
            counseling_type='교수상담',
            counseling_category=random.choice(['학업', '진로', '심리']),
            status='완료',
            location='상담실 A',
            request_content=random.choice(REQ_TEXT),
            result_content=random.choice(RES_TEXT),
            contact_number=student.user.phone
        )

# 학부모 → 교사 상담
for student in students:
    parent_student = ParentStudent.objects.filter(student=student).first()
    if parent_student:
        parent = parent_student.parent
        Counseling.objects.create(
            student=student,
            teacher=teacher,
            counseling_date=datetime(2025, 5, random.randint(10, 12)),
            counseling_time=time(random.randint(9, 17), random.choice([0, 30])),
            counseling_type='글쓰기상담',
            counseling_category=random.choice(['학업', '진로', '심리']),
            status='신청',
            location='상담실 B',
            request_content=random.choice(REQ_TEXT),
            result_content='',
            contact_number=parent.user.phone
        )

        for _ in range(random.randint(1, 2)):
            Counseling.objects.create(
                student=student,
                teacher=teacher,
                counseling_date=fake.date_between_dates(datetime(2025, 3, 1), TODAY),
                counseling_time=time(random.randint(9, 17), random.choice([0, 30])),
                counseling_type='글쓰기상담',
                counseling_category=random.choice(['학업', '진로', '심리']),
                status='완료',
                location='상담실 B',
                request_content=random.choice(REQ_TEXT),
                result_content=random.choice(RES_TEXT),
                contact_number=parent.user.phone
            )

print("✅ dummy_data2.py 실행 완료: 2학년 1반 학생 및 학부모 더미 데이터 생성 완료")
