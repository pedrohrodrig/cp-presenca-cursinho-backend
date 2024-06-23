from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from .models import Lesson, LessonSession
from .serializers import LessonSerializer, AttendanceRegistrabilitySerializer

# Create your views here.

class LessonView(ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class AttendanceRegistrabilityView(ViewSet):
    
    def update_attendance_registrability(self, request, pk):

        lesson_session = get_object_or_404(LessonSession.objects.all(), pk=pk)

        lesson_session.is_attendance_registrable = not lesson_session.is_attendance_registrable 
        lesson_session.save()

        return Response(status=status.HTTP_200_OK)
