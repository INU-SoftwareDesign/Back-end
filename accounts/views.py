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

User = get_user_model()

class SignUpView(APIView):
    @transaction.atomic
    def post(self, request):
        data = request.data

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
            classroom = Classroom.objects.filter(grade=data["grade"], class_number=data["class"]).first()
            if classroom:
                classroom.teacher = Teacher.objects.get(user=user)
                classroom.save()

            for subject_name in data["subjects"]:
                subject = Subject.objects.filter(name=subject_name).first()
                if subject:
                    subject.teacher = Teacher.objects.get(user=user)
                    subject.save()

        elif role == "student":
            classroom = Classroom.objects.filter(grade=data["grade"], class_number=data["class"]).first()
            student = Student.objects.create(
                user=user,
                classroom=classroom,
                student_number=data["number"],
                student_id=data["studentId"]
            )
            StudentClassHistory.objects.create(
                student=student,
                grade=data["grade"],
                class_number=data["class"],
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

        return Response({"message": "User registered successfully", "userId": user.username}, status=201)


class LoginView(APIView):
    def post(self, request):
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
                "class": classroom.class_number if classroom else None
            })

        elif user.role == "student":
            student = Student.objects.get(user=user)
            classroom = student.classroom
            base_data.update({
                "grade": classroom.grade if classroom else None,
                "class": classroom.class_number if classroom else None,
                "number": student.student_number,
                "childStudentId": student.student_id
            })

        elif user.role == "parent":
            parent = ParentStudent.objects.filter(parent__user=user).first()
            if parent:
                student = parent.student
                classroom = student.classroom
                base_data.update({
                    "grade": classroom.grade if classroom else None,
                    "class": classroom.class_number if classroom else None,
                    "childStudentId": student.student_id
                })

        return Response({
            "token": str(refresh.access_token),
            "refresh": str(refresh),
            "user": base_data
        }, status=200)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({"message": "Invalid token"}, status=400)

        return Response({"message": "Successfully logged out"}, status=200)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get("currentPassword")
        new_password = request.data.get("newPassword")

        if not user.check_password(current_password):
            return Response({"error": "Current password is incorrect"}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password changed successfully"}, status=200)

class UserUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
