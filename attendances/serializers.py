from rest_framework import serializers
from .models import AttendanceRecord, AttendanceSummary
from students.models import Student

class AttendanceDetailSerializer(serializers.Serializer):
    date = serializers.DateField()
    reason = serializers.CharField()

class AttendanceTypeDetailSerializer(serializers.Serializer):
    illness = AttendanceDetailSerializer(many=True)
    unauthorized = AttendanceDetailSerializer(many=True)
    etc = AttendanceDetailSerializer(many=True)

class AttendanceGroupSerializer(serializers.Serializer):
    absence = AttendanceTypeDetailSerializer()
    lateness = AttendanceTypeDetailSerializer()
    earlyLeave = AttendanceTypeDetailSerializer()
    result = AttendanceTypeDetailSerializer()

class AttendanceStatSerializer(serializers.Serializer):
    illness = serializers.IntegerField()
    unauthorized = serializers.IntegerField()
    etc = serializers.IntegerField()

class AttendanceTypeStatSerializer(serializers.Serializer):
    absence = AttendanceStatSerializer()
    lateness = AttendanceStatSerializer()
    earlyLeave = AttendanceStatSerializer()
    result = AttendanceStatSerializer()

class AttendanceResponseSerializer(serializers.Serializer):
    grade = serializers.CharField()
    year = serializers.IntegerField()
    homeTeacher = serializers.CharField(allow_null=True)
    totalDays = serializers.IntegerField()
    remarks = serializers.CharField(allow_null=True)
    attendance = AttendanceTypeStatSerializer()
    details = AttendanceGroupSerializer()

class AttendanceListResponseSerializer(serializers.Serializer):
    studentId = serializers.IntegerField()
    studentName = serializers.CharField()
    attendance = AttendanceResponseSerializer(many=True)
