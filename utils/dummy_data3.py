import random
from faker import Faker
from django.utils import timezone

# Django 모델 임포트
from accounts.models import User
from students.models import Student, StudentClassHistory
from teachers.models import Teacher
from classrooms.models import Classroom
from feedbacks.models import FeedbackGroup, Feedback
from specialnotes.models import SpecialNote

fake = Faker('ko_KR')

# 2학년 1반에 속한 모든 학생 조회
classroom_2_1 = Classroom.objects.get(grade=2, class_number=1)
students_2_1 = Student.objects.filter(classroom=classroom_2_1)

# 피드백 샘플 문장/데이터 정의 (긍정적 + 비판적 문장 포함)
feedback_categories = ["academic", "behavior", "attendance", "attitude"]
sample_feedback_texts = {
    "academic": [
        # 긍정적
        "학업 성취도가 매우 우수하며 자기주도 학습 능력이 뛰어납니다.",
        "최근 수학 과목에서 눈에 띄는 발전을 보이고 있습니다.",
        "영어 듣기 실력이 향상되어 교사 평가가 긍정적입니다.",
        # 비판적
        "최근 수학 성적이 하락 추세이니 기본 개념을 다시 복습할 필요가 있습니다.",
        "영어 과목 과제 제출이 늦는 경우가 많아 학습 태도를 개선해야 합니다.",
        "과학 실험 보고서 작성 시 논리 전개가 부족하여 보완이 필요합니다."
    ],
    "behavior": [
        # 긍정적
        "수업 태도가 모범적이며 친구들과의 협동심이 뛰어납니다.",
        "교내 봉사활동에 적극적으로 참여하여 모범적인 태도를 보입니다.",
        "수업 중 발표 시간에 자신감 있게 의견을 나누고 있습니다.",
        # 비판적
        "수업 중 잡담이 잦아 집중력이 떨어지는 모습이 보입니다.",
        "친구들과의 규칙을 지키지 않아 학급 운영에 방해가 되는 경우가 있습니다.",
        "과제 제출 시 협업 태도가 미흡하여 팀 활동에서 갈등이 발생하기도 합니다."
    ],
    "attendance": [
        # 긍정적
        "출석 상황이 매우 양호하며 결석 없이 등교하고 있습니다.",
        "지각 없이 정시에 등교하여 학습에 열의를 보이고 있습니다.",
        "조퇴나 결석 없이 꾸준히 출석하고 있습니다.",
        # 비판적
        "최근 지각 횟수가 잦아 시간 관리에 문제가 있는 것으로 보입니다.",
        "결석 사유를 미리 알리지 않아 결석 처리 절차 개선이 필요합니다.",
        "결석 후 보충 학습 계획이 미흡하여 학업 공백이 발생하고 있습니다."
    ],
    "attitude": [
        # 긍정적
        "항상 긍정적인 마인드로 수업에 임하며 학습 의지가 강합니다.",
        "문제 해결에 대한 호기심이 많아 스스로 질문하고 탐구하려는 태도를 보입니다.",
        "친구들을 배려하는 태도로 학급 분위기를 좋게 만듭니다.",
        # 비판적
        "수업 분위기에 다소 소극적이며 질문 참여가 부족한 편입니다.",
        "새로운 과제에 대한 도전 의식이 낮아 성장 가능성이 제한될 수 있습니다.",
        "협업 시 자신의 의견만 고집하여 팀워크에 부정적인 영향을 미치는 경우가 있습니다."
    ]
}

# 특기사항에 사용할 샘플 데이터
special_talents = ["음악", "체육", "미술", "과학", "독서", "코딩", "연극", "춤"]
career_aspirations = [
    {"student": "의사", "parent": "교수"},
    {"student": "변호사", "parent": "판사"},
    {"student": "공학자", "parent": "연구원"},
    {"student": "예술가", "parent": "디자이너"},
    {"student": "프로그래머", "parent": "IT 엔지니어"},
    {"student": "교사", "parent": "교육자"},
    {"student": "운동선수", "parent": "코치"}
]
sample_note_texts = [
    "항상 책임감 있게 활동에 참여하며 뛰어난 성실성을 보입니다.",
    "창의적인 사고를 통해 문제 해결 능력이 뛰어나며, 협업도 원만히 수행합니다.",
    "도전 정신이 강해 새로운 학습 과제에도 적극적으로 임합니다.",
    "친구들을 배려하는 따뜻한 마음을 지니고 있어 학급 분위기를 좋게 만듭니다."
]

#############################################
# 1) 1학년 피드백(과거 학년) 추가
#############################################
for student in students_2_1:
    # 학생의 1학년 학급 이력 가져오기
    history_1 = StudentClassHistory.objects.filter(student=student, grade=1).first()
    if history_1:
        # 1학년 당시 담임 교사 조회
        try:
            classroom_1 = Classroom.objects.get(grade=1, class_number=history_1.class_number)
            teacher_1 = classroom_1.teacher
        except Classroom.DoesNotExist:
            teacher_1 = random.choice(Teacher.objects.all())
    else:
        teacher_1 = random.choice(Teacher.objects.all())

    # FeedbackGroup(1학년) 생성
    fg_1 = FeedbackGroup.objects.create(
        student=student,
        grade=1,
        class_number=(history_1.class_number if history_1 else 1),
        teacher=teacher_1
    )

    # Feedback 5개 생성 (긍정·부정 섞어서 랜덤)
    for _ in range(5):
        category = random.choice(feedback_categories)
        content = random.choice(sample_feedback_texts[category])
        Feedback.objects.create(
            feedback_group=fg_1,
            category=category,
            content=content
        )

#############################################
# 2) 2학년 피드백(현재 학년) 추가
#############################################
for student in students_2_1:
    # 2학년 1반 담임 교사
    teacher_2 = classroom_2_1.teacher

    # FeedbackGroup(2학년) 생성
    fg_2 = FeedbackGroup.objects.create(
        student=student,
        grade=2,
        class_number=1,
        teacher=teacher_2
    )

    # Feedback 2개 생성 (긍정·부정 섞어서 랜덤)
    for _ in range(2):
        category = random.choice(feedback_categories)
        content = random.choice(sample_feedback_texts[category])
        Feedback.objects.create(
            feedback_group=fg_2,
            category=category,
            content=content
        )

#############################################
# 3) 특기사항 생성 (1학년, 2학년 각각 1개씩)
#############################################
for student in students_2_1:
    # 1학년 특기사항
    history_1 = StudentClassHistory.objects.filter(student=student, grade=1).first()
    if history_1:
        try:
            classroom_1 = Classroom.objects.get(grade=1, class_number=history_1.class_number)
            teacher_1 = classroom_1.teacher
        except Classroom.DoesNotExist:
            teacher_1 = random.choice(Teacher.objects.all())
        teacher_name_1 = teacher_1.user.name if teacher_1 else fake.name()
        special_talent_1 = random.choice(special_talents)
        career_aspiration_1 = random.choice(career_aspirations)
        note_1 = random.choice(sample_note_texts)

        SpecialNote.objects.create(
            student=student,
            grade=1,
            class_number=history_1.class_number,
            teacher=teacher_1,
            teacher_name=teacher_name_1,
            special_talent=special_talent_1,
            career_aspiration=career_aspiration_1,
            note=note_1
        )

    # 2학년 특기사항
    teacher_name_2 = classroom_2_1.teacher.user.name if classroom_2_1.teacher else fake.name()
    special_talent_2 = random.choice(special_talents)
    career_aspiration_2 = random.choice(career_aspirations)
    note_2 = random.choice(sample_note_texts)

    SpecialNote.objects.create(
        student=student,
        grade=2,
        class_number=1,
        teacher=classroom_2_1.teacher,
        teacher_name=teacher_name_2,
        special_talent=special_talent_2,
        career_aspiration=career_aspiration_2,
        note=note_2
    )

print("✅ 2학년 1반 학생 대상 피드백 및 특기사항 더미 데이터 생성 완료")
