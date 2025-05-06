from rest_framework import generics
from .models import User
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from students.models import Student, StudentClassHistory
from teachers.models import Teacher
from parents.models import Parent, ParentStudent
from classrooms.models import Classroom
from subjects.models import Subject
from django.db import transaction
from utils.social import get_user_info
from utils.slack import send_success_slack, send_error_slack
from datetime import datetime

User = get_user_model()

class SignUpView(APIView):
    @transaction.atomic
    def post(self, request):
        start_time = datetime.now()
        data = request.data

        try:
            if User.objects.filter(username=data["id"]).exists():
                return Response({"error": "User ID already exists"}, status=400)

            user = User.objects.create(
                username=data["id"],
                password=make_password(data["password"]),
                name=data["name"],
                phone=data["phone"],
                birth_date=data.get("birth_date"),
                address=data.get("address"),
                role=data["role"],
                is_active=False,
                approval_status="pending"
            )

            role = data["role"]

            if role == "teacher":
                Teacher.objects.create(user=user, teacher_code=data["teacherCode"])
                classroom = Classroom.objects.filter(grade=data["grade"], class_number=data["classNumber"]).first()
                if classroom:
                    classroom.teacher = Teacher.objects.get(user=user)
                    classroom.save()

                for subject_name in data["subjects"]:
                    subject = Subject.objects.filter(name=subject_name).first()
                    if subject:
                        subject.teacher = Teacher.objects.get(user=user)
                        subject.save()

            elif role == "student":
                classroom = Classroom.objects.filter(grade=data["grade"], class_number=data["classNumber"]).first()
                student = Student.objects.create(
                    user=user,
                    classroom=classroom,
                    student_number=data["number"],
                    student_id=data["studentId"]
                )
                StudentClassHistory.objects.create(
                    student=student,
                    grade=data["grade"],
                    class_number=data["classNumber"],
                    number=data["number"],
                    homeroom_teacher=classroom.teacher.user.name if classroom and classroom.teacher else ""
                )

            elif role == "parent":
                parent = Parent.objects.create(user=user)
                student = Student.objects.filter(student_id=data["childStudentId"]).first()
                if student:
                    ParentStudent.objects.create(
                        parent=parent,
                        student=student,
                        role="father" if data["relationship"] == "아버지" else "mother"
                    )

            send_success_slack(request, "회원가입", start_time)
            return Response({"message": "User registered successfully", "userId": user.username}, status=201)

        except Exception as e:
            send_error_slack(request, "회원가입", start_time)
            return Response({"error": str(e)}, status=500)

class LoginView(APIView):
    def post(self, request):
        start_time = datetime.now()
        try:
            username = request.data.get("id")
            password = request.data.get("password")
            user = authenticate(username=username, password=password)

            if not user or not user.is_active:
                return Response({"error": "Invalid credentials"}, status=401)

            refresh = RefreshToken.for_user(user)
            base_data = {
                "id": user.username,
                "name": user.name,
                "role": user.role
            }

            if user.role == "teacher":
                teacher = Teacher.objects.get(user=user)
                classroom = getattr(teacher, "classroom", None)
                base_data.update({
                    "grade": classroom.grade if classroom else None,
                    "classNumber": classroom.class_number if classroom else None
                })

            elif user.role == "student":
                student = Student.objects.get(user=user)
                classroom = student.classroom
                base_data.update({
                    "grade": classroom.grade if classroom else None,
                    "classNumber": classroom.class_number if classroom else None,
                    "number": student.student_number,
                    "studentId": student.student_id
                })

            elif user.role == "parent":
                parent = ParentStudent.objects.filter(parent__user=user).first()
                if parent:
                    student = parent.student
                    classroom = student.classroom
                    base_data.update({
                        "grade": classroom.grade if classroom else None,
                        "classNumber": classroom.class_number if classroom else None,
                        "childStudentId": student.student_id
                    })

            send_success_slack(request, "로그인", start_time)
            return Response({
                "token": str(refresh.access_token),
                "refresh": str(refresh),
                "user": base_data
            }, status=200)

        except Exception as e:
            send_error_slack(request, "로그인", start_time)
            return Response({"error": str(e)}, status=500)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        start_time = datetime.now()
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            send_success_slack(request, "로그아웃", start_time)
            return Response({"message": "Successfully logged out"}, status=200)
        except Exception as e:
            send_error_slack(request, "로그아웃", start_time)
            return Response({"error": str(e)}, status=400)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        start_time = datetime.now()
        user = request.user

        try:
            if user.social_type:
                return Response(
                    {"error": "소셜 로그인 사용자는 비밀번호를 변경할 수 없습니다."},
                    status=403
                )

            current_password = request.data.get("currentPassword")
            new_password = request.data.get("newPassword")

            if not user.check_password(current_password):
                return Response({"error": "Current password is incorrect"}, status=400)

            user.set_password(new_password)
            user.save()

            send_success_slack(request, "비밀번호 변경", start_time)
            return Response({"message": "Password changed successfully"}, status=200)

        except Exception as e:
            send_error_slack(request, "비밀번호 변경", start_time)
            return Response({"error": str(e)}, status=500)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def get_object(self):
        return self.request.user

    def get(self, request):
        start_time = datetime.now()
        try:
            user = request.user
            data = {
                "id": user.username,
                "username": user.username,
                "role": user.role,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "birth_date": user.birth_date,
                "address": user.address,
                "social_type": user.social_type,
            }

            if user.role == "teacher":
                teacher = Teacher.objects.get(user=user)
                classroom = Classroom.objects.filter(teacher=teacher).first()
                data.update({
                    "grade": classroom.grade if classroom else None,
                    "classNumber": classroom.class_number if classroom else None,
                    "subjects": list(Subject.objects.filter(teacher=teacher).values_list("name", flat=True)),
                    "teacherCode": teacher.teacher_code
                })

            elif user.role == "student":
                student = Student.objects.get(user=user)
                classroom = student.classroom
                data.update({
                    "grade": classroom.grade if classroom else None,
                    "classNumber": classroom.class_number if classroom else None,
                    "number": student.student_number,
                    "studentId": student.student_id
                })

            elif user.role == "parent":
                parent_relation = ParentStudent.objects.filter(parent__user=user).first()
                if parent_relation:
                    student = parent_relation.student
                    classroom = student.classroom
                    data.update({
                        "childStudentId": student.student_id,
                        "relationship": parent_relation.role,
                    })

            send_success_slack(request, "유저 정보 조회", start_time)
            return Response(data)

        except Exception as e:
            send_error_slack(request, "유저 정보 조회", start_time)
            return Response({"error": str(e)}, status=500)

    def put(self, request):
        start_time = datetime.now()
        try:
            user = request.user
            allowed_fields = ['name', 'email', 'phone', 'birth_date', 'address']
            for field in allowed_fields:
                if field in request.data:
                    setattr(user, field, request.data[field])
            user.save()
            send_success_slack(request, "유저 정보 수정", start_time)
            return Response({"message": "profile updated successfully"})
        except Exception as e:
            send_error_slack(request, "유저 정보 수정", start_time)
            return Response({"error": str(e)}, status=500)
    
class SocialLoginView(APIView):
    def post(self, request):
        start_time = datetime.now()
        provider = request.data.get("provider")
        access_token = request.data.get("access_token")

        if not provider or not access_token:
            return Response({"error": "provider와 access_token은 필수입니다."}, status=400)

        try:
            user_info = get_user_info(provider, access_token)
        except Exception as e:
            send_error_slack(request, "소셜 로그인", start_time)
            return Response({"error": f"{provider} 사용자 정보 조회 실패: {str(e)}"}, status=400)

        try:
            social_id = user_info["id"]
            email = user_info["email"]
            name = user_info["name"]

            user, created = User.objects.get_or_create(
                social_type=provider,
                social_id=social_id,
                defaults={
                    "username": f"{provider}_{social_id}",
                    "email": email,
                    "name": name,
                    "is_active": False,
                    "approval_status": "pending",
                }
            )

            if not user.is_active or user.approval_status != "approved":
                send_success_slack(request, "소셜 로그인 - 추가 정보 필요", start_time)
                return Response({
                    "message": "추가 정보를 등록해주세요.",
                    "userId": user.username,
                    "requiresAdditionalInfo": created
                }, status=200)

            refresh = RefreshToken.for_user(user)

            base_data = {
                "id": user.username,
                "name": user.name,
                "role": user.role
            }

            if user.role == "teacher":
                teacher = Teacher.objects.get(user=user)
                classroom = getattr(teacher, "classroom", None)
                base_data.update({
                    "grade": classroom.grade if classroom else None,
                    "classNumber": classroom.class_number if classroom else None
                })

            elif user.role == "student":
                student = Student.objects.get(user=user)
                classroom = student.classroom
                base_data.update({
                    "grade": classroom.grade if classroom else None,
                    "classNumber": classroom.class_number if classroom else None,
                    "number": student.student_number,
                    "childStudentId": student.student_id
                })

            elif user.role == "parent":
                parent_relation = ParentStudent.objects.filter(parent__user=user).first()
                if parent_relation:
                    student = parent_relation.student
                    classroom = student.classroom
                    base_data.update({
                        "grade": classroom.grade if classroom else None,
                        "classNumber": classroom.class_number if classroom else None,
                        "childStudentId": student.student_id
                    })

            send_success_slack(request, "소셜 로그인", start_time)
            return Response({
                "token": str(refresh.access_token),
                "refresh": str(refresh),
                "user": base_data
            }, status=200)

        except Exception as e:
            send_error_slack(request, "소셜 로그인", start_time)
            return Response({"error": str(e)}, status=500)


class SocialRegisterDetailView(APIView):
    def post(self, request):
        start_time = datetime.now()
        data = request.data
        user_id = data.get("userId")
        role = data.get("role")

        if not user_id or not role:
            return Response({"error": "userId와 role은 필수입니다."}, status=400)

        try:
            user = User.objects.get(username=user_id)
        except User.DoesNotExist:
            send_error_slack(request, "소셜 회원 추가 정보 등록", start_time)
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=404)

        if user.is_active:
            send_error_slack(request, "소셜 회원 추가 정보 등록", start_time)
            return Response({"error": "이미 활성화된 사용자입니다."}, status=400)

        user.role = role
        user.name = data.get("name", user.name)
        user.phone = data.get("phone", user.phone)
        user.birth_date = data.get("birth_date", user.birth_date)
        user.address = data.get("address", user.address)
        user.save()

        try:
            if role == "student":
                classroom = Classroom.objects.filter(
                    grade=data.get("grade"), class_number=data.get("classNumber")
                ).first()
                if not classroom:
                    send_error_slack(request, "소셜 회원 추가 정보 등록", start_time)
                    return Response({"error": "해당 반이 존재하지 않습니다."}, status=400)

                student = Student.objects.create(
                    user=user,
                    classroom=classroom,
                    student_number=data["number"],
                    student_id=data["studentId"]
                )
                StudentClassHistory.objects.create(
                    student=student,
                    grade=classroom.grade,
                    class_number=classroom.class_number,
                    number=data["number"],
                    homeroom_teacher=classroom.teacher.user.name if classroom.teacher else ""
                )

            elif role == "teacher":
                Teacher.objects.create(user=user, teacher_code=data["teacherCode"])

                classroom = Classroom.objects.filter(
                    grade=data.get("grade"), class_number=data.get("classNumber")
                ).first()
                if classroom:
                    classroom.teacher = Teacher.objects.get(user=user)
                    classroom.save()

                for subject_name in data.get("subjects", []):
                    subject = Subject.objects.filter(name=subject_name).first()
                    if subject:
                        subject.teacher = Teacher.objects.get(user=user)
                        subject.save()

            elif role == "parent":
                parent = Parent.objects.create(user=user)
                student = Student.objects.filter(student_id=data["childStudentId"]).first()
                if student:
                    ParentStudent.objects.create(
                        parent=parent,
                        student=student,
                        role="father" if data["relationship"] == "아버지" else "mother"
                    )
                else:
                    send_error_slack(request, "소셜 회원 추가 정보 등록", start_time)
                    return Response({"error": "해당 학생을 찾을 수 없습니다."}, status=404)

            send_success_slack(request, "소셜 회원 추가 정보 등록", start_time)
            return Response({"message": "추가 정보 등록 완료. 관리자 승인을 기다려주세요."}, status=201)

        except Exception as e:
            send_error_slack(request, "소셜 회원 추가 정보 등록", start_time)
            return Response({"error": str(e)}, status=500)