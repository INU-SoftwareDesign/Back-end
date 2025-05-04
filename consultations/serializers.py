from rest_framework import serializers
from .models import Counseling
from students.models import Student
from teachers.models import Teacher

class CounselingSerializer(serializers.ModelSerializer):
    studentId = serializers.IntegerField(source='student.id')
    studentName = serializers.CharField(source='student.user.name')
    grade = serializers.IntegerField(source='student.classroom.grade')
    classNumber = serializers.IntegerField(source='student.classroom.class_number')
    number = serializers.IntegerField(source='student.student_number')
    counselorName = serializers.CharField(source='teacher.user.name')

    requestDate = serializers.DateField(source='request_date', format='%Y-%m-%d')
    counselingDate = serializers.DateField(source='counseling_date', format='%Y-%m-%d')
    counselingTime = serializers.SerializerMethodField()

    counselingType = serializers.CharField(source='counseling_type')
    counselingCategory = serializers.CharField(source='counseling_category')
    requestContent = serializers.CharField(source='request_content')
    resultContent = serializers.SerializerMethodField()
    contactNumber = serializers.CharField(source='contact_number')

    class Meta:
        model = Counseling
        fields = [
            'id', 'studentId', 'studentName', 'grade', 'classNumber', 'number',
            'requestDate', 'counselingDate', 'counselingTime', 'counselorName',
            'counselingType', 'counselingCategory', 'status', 'location',
            'requestContent', 'resultContent', 'contactNumber'
        ]

    def get_counselingTime(self, obj):
        return obj.counseling_time.strftime('%H:%M')
    
    def get_resultContent(self, obj):
        return obj.result_content or ""

class TeacherCounselingRequestSerializer(serializers.ModelSerializer):
    studentId = serializers.IntegerField(source='student.id')
    studentName = serializers.CharField(source='student.user.name')
    grade = serializers.IntegerField(source='student.classroom.grade')
    classNumber = serializers.IntegerField(source='student.classroom.class_number')
    number = serializers.IntegerField(source='student.student_number')

    requestDate = serializers.DateField(source='request_date', format='%Y-%m-%d')
    counselingDate = serializers.DateField(source='counseling_date', format='%Y-%m-%d')
    counselingTime = serializers.SerializerMethodField()

    counselingType = serializers.CharField(source='counseling_type')
    counselingCategory = serializers.CharField(source='counseling_category')
    requestContent = serializers.CharField(source='request_content')
    contactNumber = serializers.CharField(source='contact_number')

    class Meta:
        model = Counseling
        fields = [
            'id', 'studentId', 'studentName', 'grade', 'classNumber', 'number',
            'requestDate', 'counselingDate', 'counselingTime',
            'counselingType', 'counselingCategory', 'status',
            'requestContent', 'contactNumber'
        ]

    def get_counselingTime(self, obj):
        return obj.counseling_time.strftime('%H:%M')

class TeacherScheduledCounselingSerializer(serializers.ModelSerializer):
    studentId = serializers.IntegerField(source='student.id')
    studentName = serializers.CharField(source='student.user.name')
    grade = serializers.IntegerField(source='student.classroom.grade')
    classNumber = serializers.IntegerField(source='student.classroom.class_number')
    number = serializers.IntegerField(source='student.student_number')

    requestDate = serializers.DateField(source='request_date', format='%Y-%m-%d')
    counselingDate = serializers.DateField(source='counseling_date', format='%Y-%m-%d')
    counselingTime = serializers.SerializerMethodField()

    counselingType = serializers.CharField(source='counseling_type')
    counselingCategory = serializers.CharField(source='counseling_category')
    requestContent = serializers.CharField(source='request_content')
    resultContent = serializers.SerializerMethodField()
    contactNumber = serializers.CharField(source='contact_number')
    location = serializers.CharField()

    class Meta:
        model = Counseling
        fields = [
            'id', 'studentId', 'studentName', 'grade', 'classNumber', 'number',
            'requestDate', 'counselingDate', 'counselingTime',
            'counselingType', 'counselingCategory', 'status',
            'location', 'requestContent', 'resultContent', 'contactNumber'
        ]

    def get_counselingTime(self, obj):
        return obj.counseling_time.strftime('%H:%M')

    def get_resultContent(self, obj):
        return obj.result_content or ""

class CounselingRequestSerializer(serializers.ModelSerializer):
    studentId = serializers.IntegerField(write_only=True)
    teacherId = serializers.IntegerField(write_only=True)
    counselingDate = serializers.DateField(source='counseling_date')
    counselingTime = serializers.TimeField(source='counseling_time')
    counselingType = serializers.CharField(source='counseling_type')
    counselingCategory = serializers.CharField(source='counseling_category')
    requestContent = serializers.CharField(source='request_content')
    contactNumber = serializers.CharField(source='contact_number')

    class Meta:
        model = Counseling
        fields = [
            'studentId', 'teacherId',
            'counselingDate', 'counselingTime',
            'counselingType', 'counselingCategory',
            'requestContent', 'contactNumber'
        ]

    def validate(self, attrs):
        from students.models import Student
        from teachers.models import Teacher
        from consultations.models import Counseling

        student_id = attrs.get('studentId')
        teacher_id = attrs.get('teacherId')
        counseling_date = attrs.get('counseling_date')
        counseling_time = attrs.get('counseling_time')

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            raise serializers.ValidationError({'studentId': '존재하지 않는 학생입니다.'})

        try:
            teacher = Teacher.objects.get(id=teacher_id)
        except Teacher.DoesNotExist:
            raise serializers.ValidationError({'teacherId': '존재하지 않는 교사입니다.'})

        if Counseling.objects.filter(
            teacher=teacher,
            counseling_date=counseling_date,
            counseling_time=counseling_time
        ).exists():
            raise serializers.ValidationError({
                'non_field_errors': ['해당 시간에 이미 예약된 상담이 있습니다.']
            })

        attrs['student'] = student
        attrs['teacher'] = teacher
        return attrs

    def create(self, validated_data):
        validated_data.pop('studentId')
        validated_data.pop('teacherId')
        return Counseling.objects.create(**validated_data)

class CounselingApproveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Counseling
        fields = ['location']

    def update(self, instance, validated_data):
        instance.location = validated_data.get('location', instance.location)
        instance.status = '예약확정'
        instance.save()
        return instance


class CounselingUpdateSerializer(serializers.ModelSerializer):
    counselingDate = serializers.DateField(source='counseling_date', required=False)
    counselingTime = serializers.TimeField(source='counseling_time', required=False)
    location = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    resultContent = serializers.CharField(source='result_content', required=False, allow_blank=True)
    requestContent = serializers.CharField(source='request_content', required=False)

    class Meta:
        model = Counseling
        fields = [
            'counselingDate', 'counselingTime', 'location', 'status',
            'resultContent', 'requestContent'
        ]
