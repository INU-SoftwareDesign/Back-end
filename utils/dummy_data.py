import random
from faker import Faker
from accounts.models import User
from students.models import Student, StudentClassHistory, StudentAcademicRecord
from teachers.models import Teacher
from parents.models import Parent, ParentStudent
from classrooms.models import Classroom
from subjects.models import Subject

fake = Faker('ko_KR')

subjects = ['국어', '수학', '영어', '과학', '사회', '역사', '지리', '생명과학', '물리', '화학', '기술', '가정', '도덕', '체육', '음악']

# 교사 20명 생성
teachers = []
for i in range(20):
    user = User.objects.create_user(
        username=f'teacher{i+1}',
        password='pass1234',
        role='teacher',
        name=fake.name(),
        phone=fake.phone_number(),
        birth_date=fake.date_of_birth(minimum_age=30, maximum_age=45),
        address=fake.address(),
        is_active=True,
        approval_status='approved'
    )
    teacher = Teacher.objects.create(user=user, teacher_code=f'T2025-{i+1:03}')
    teachers.append(teacher)

# 학급 생성 (1~3학년 × 4반 = 12반), homeroom 담당은 앞에서 12명만
classrooms = []
for i in range(12):
    grade = (i // 4) + 1
    class_number = (i % 4) + 1
    homeroom_teacher = teachers[i]
    classroom = Classroom.objects.create(
        grade=grade,
        class_number=class_number,
        teacher=homeroom_teacher
    )
    classrooms.append(classroom)

# 학생 250명 생성
students = []
for i in range(250):
    name = fake.name()
    username = f'student{i+1}'
    student_id = f'2025{i+1:04}'
    user = User.objects.create_user(
        username=username,
        password='pass1234',
        role='student',
        name=name,
        phone=fake.phone_number(),
        birth_date=fake.date_of_birth(minimum_age=14, maximum_age=17),
        address=fake.address(),
        is_active=True,
        approval_status='approved'
    )
    classroom = random.choice(classrooms)
    student_number = random.randint(1, 30)
    student = Student.objects.create(
        user=user,
        classroom=classroom,
        student_number=student_number,
        student_id=student_id
    )

    current_grade = classroom.grade
    for past_grade in range(1, current_grade):
        StudentClassHistory.objects.create(
            student=student,
            grade=past_grade,
            class_number=random.randint(1, 4),
            number=student_number,
            homeroom_teacher=fake.name()
        )

    StudentAcademicRecord.objects.create(student=student, description="2015년 3월 2일 소설초등학교 제1학년 입학")
    StudentAcademicRecord.objects.create(student=student, description="2021년 2월 10일 소설초등학교 졸업")
    StudentAcademicRecord.objects.create(student=student, description="2021년 3월 2일 소설중학교 제1학년 입학")
    StudentAcademicRecord.objects.create(student=student, description="2024년 2월 10일 소설중학교 졸업")

    for g in range(1, current_grade + 1):
        description = f"{2023 + g}년 3월 2일 소설고등학교 제{g}학년 진급" if g != 1 else "2024년 3월 2일 소설고등학교 제1학년 입학"
        StudentAcademicRecord.objects.create(student=student, description=description)

    students.append(student)

# 학부모 생성 및 자녀 연결
for i in range(50):
    user = User.objects.create_user(
        username=f'parent{i+1}',
        password='pass1234',
        role='parent',
        name=fake.name(),
        phone=fake.phone_number(),
        birth_date=fake.date_of_birth(minimum_age=40, maximum_age=50),
        address=fake.address(),
        is_active=True,
        approval_status='approved'
    )
    parent = Parent.objects.create(user=user)
    for student in random.sample(students, k=random.randint(1, 2)):
        ParentStudent.objects.get_or_create(
            parent=parent,
            student=student,
            defaults={'role': random.choice(['father', 'mother'])}
        )

# 과목 15개 생성 → 교사 20명 중 15명에게 1개씩 배정
for i, subject_name in enumerate(subjects):
    Subject.objects.create(
        name=subject_name,
        teacher=teachers[i]  # 0~14번 교사만 과목 담당
    )

print("✅ 더미 데이터 생성 완료!")
