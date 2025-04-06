from rest_framework import serializers
from .models import Grade
from subjects.models import Subject

class GradeSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source='subject.name', read_only=True)
    subject_id = serializers.IntegerField(write_only=True)
    grade_letter = serializers.SerializerMethodField()

    class Meta:
        model = Grade
        fields = ['id', 'subject', 'subject_id', 'semester', 'score', 'grade_letter']

    def get_grade_letter(self, obj):
        score = obj.score
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
