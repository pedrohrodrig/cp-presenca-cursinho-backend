from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from .models import Attendance, Lesson, Student, Subject
from .serializers import AttendanceSerializer, LessonPasskeySerializer, LessonSerializer, LessonWithDetailsSerializer, StudentSerializer, SubjectSerializer

# Create your views here.


class LessonView(ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def list_next_lessons_with_details(self, request):
        queryset = Lesson.objects.filter(start_datetime__gte=datetime.now())

        lessons_list_serialized = LessonWithDetailsSerializer(queryset, many=True)

        return Response(lessons_list_serialized.data, status=status.HTTP_200_OK)
    
    def update_passkey(self, request, pk):
        lesson = get_object_or_404(Lesson.objects.all(), pk=pk)

        lesson.passkey = request.passkey
        lesson.save()
        lesson_serialized = LessonSerializer(lesson)

        return Response(lesson_serialized.data, status=status.HTTP_200_OK)


class AttendanceRegistrabilityView(ViewSet):
    def update_attendance_registrability(self, request, pk):
        lesson = get_object_or_404(Lesson.objects.all(), pk=pk)

        lesson.is_attendance_registrable = not lesson.is_attendance_registrable
        lesson.save()

        lesson_serialized = LessonPasskeySerializer(lesson)

        return Response(lesson_serialized.data, status=status.HTTP_200_OK)


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


class StudentView(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class SubjectView(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = SubjectSerializer
