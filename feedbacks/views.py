from rest_framework import generics
from .models import Feedback
from .serializers import FeedbackSerializer

class FeedbackView(generics.ListCreateAPIView):
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        student_id = self.request.query_params.get('student_id')
        return Feedback.objects.filter(student_id=student_id).select_related('student__user', 'teacher__user')

class FeedbackDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Feedback.objects.select_related('student__user', 'teacher__user')
    serializer_class = FeedbackSerializer
