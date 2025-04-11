from rest_framework import generics
from .models import Consultation
from .serializers import ConsultationSerializer

class ConsultationView(generics.ListCreateAPIView):
    serializer_class = ConsultationSerializer

    def get_queryset(self):
        student_id = self.request.query_params.get('student_id')
        if student_id:
            return Consultation.objects.filter(student_id=student_id).select_related('student__user', 'teacher__user')
        return Consultation.objects.all().select_related('student__user', 'teacher__user')

class ConsultationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Consultation.objects.select_related('student__user', 'teacher__user')
    serializer_class = ConsultationSerializer
