from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from .models import Attendance, Lesson, LessonSession
from .serializers import AttendanceSerializer, LessonSerializer, LessonSessionSerializer

# Create your views here.


class LessonView(ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class AttendanceRegistrabilityView(ViewSet):
    def update_attendance_registrability(self, request, pk):
        lesson_session = get_object_or_404(LessonSession.objects.all(), pk=pk)

        lesson_session.is_attendance_registrable = not lesson_session.is_attendance_registrable
        lesson_session.save()

        lesson_session_serialized = LessonSessionSerializer(lesson_session)

        return Response(lesson_session_serialized.data, status=status.HTTP_200_OK)


class AttendanceView(ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def create(self, request):
        serializer = AttendanceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        lesson_session = serializer.validated_data["lesson_session"]

        if not lesson_session.is_attendance_registrable:
            # TODO: melhorar codigo de erro para usuario
            return Response("Attendance is not registrable", status=status.HTTP_403_FORBIDDEN)

        attendance = Attendance.objects.create(**serializer.validated_data)
        attendance_serialized = AttendanceSerializer(attendance)

        return Response(attendance_serialized.data, status=status.HTTP_201_CREATED)
