from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from .models import Attendance, Lesson, LessonRecurrency, Student, StudentClass, Subject
from .serializers import (
    AttendanceSerializer,
    LessonPasskeySerializer,
    LessonRecurrencySerializer,
    LessonSerializer,
    LessonWithDetailsSerializer,
    StudentClassSerializer,
    StudentSerializer,
    SubjectSerializer,
)

# Create your views here.


class LessonView(ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def retrieve(self, request, pk):
        lesson = Lesson.objects.filter(pk=pk).first()
        if not lesson:
            return Response(status=status.HTTP_404_NOT_FOUND)

        lesson_serialized = LessonWithDetailsSerializer(lesson)

        return Response(lesson_serialized.data, status=status.HTTP_200_OK)

    def list_lessons_with_details(self, request):
        queryset = Lesson.objects.all()
        lessons_list_serialized = LessonWithDetailsSerializer(queryset, many=True)

        return Response(lessons_list_serialized.data, status=status.HTTP_200_OK)

    def list_today_lessons_with_details(self, request):
        now = timezone.now()
        queryset = Lesson.objects.filter(start_datetime__day=now.day).order_by("start_datetime")

        lessons_list_serialized = LessonWithDetailsSerializer(queryset, many=True)

        return Response(lessons_list_serialized.data, status=status.HTTP_200_OK)

    def update_passkey(self, request, pk):
        lesson = get_object_or_404(Lesson.objects.all(), pk=pk)

        lesson.passkey = request.passkey
        lesson.save()
        lesson_serialized = LessonPasskeySerializer(lesson)

        return Response(lesson_serialized.data, status=status.HTTP_200_OK)


class AttendanceRegistrabilityView(ViewSet):
    def update_attendance_registrability(self, request, pk):
        lesson = get_object_or_404(Lesson.objects.all(), pk=pk)

        lesson.is_manual_attendance_checked = not lesson.is_attendance_registrable
        lesson.manual_attendance_last_time_edited = timezone.now()
        lesson.save()

        lesson_serialized = LessonSerializer(lesson)

        return Response(lesson_serialized.data, status=status.HTTP_200_OK)


class AttendanceView(ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def create(self, request):
        serializer = AttendanceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        lesson = serializer.validated_data["lesson"]
        student = serializer.validated_data["student"]

        if not lesson.is_attendance_registrable:
            # TODO: melhorar codigo de erro para usuario
            return Response("Attendance is not registrable", status=status.HTTP_403_FORBIDDEN)

        if lesson.lesson_recurrency.student_class != student.student_class:
            return Response("Student do not belong to class", status=status.HTTP_403_FORBIDDEN)

        attendance, created = Attendance.objects.get_or_create(**serializer.validated_data)

        if not created:
            # TODO: melhorar codigo de erro para usuario
            return Response("Attendance already registered", status=status.HTTP_400_BAD_REQUEST)

        attendance_serialized = AttendanceSerializer(attendance)

        return Response(attendance_serialized.data, status=status.HTTP_201_CREATED)


class StudentView(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class SubjectView(ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

    def create_subject_and_recurrency(self, request):
        serializer = SubjectSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        subject = Subject.objects.create(**serializer.validated_data)
        student_classes = StudentClass.objects.all()

        for student_class in student_classes:
            recurrency_data = {
                "subject": subject.id,
                "student_class": student_class.id,
            }

            serializer = LessonRecurrencySerializer(data=recurrency_data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            LessonRecurrency.objects.create(**serializer.validated_data)

        subject_serialized = SubjectSerializer(subject)
        return Response(subject_serialized.data, status=status.HTTP_201_CREATED)

    def list_from_main_subject(self, request, main_subject):
        subjects = Subject.objects.filter(main_subject=main_subject)

        if not subjects:
            return Response(status=status.HTTP_404_NOT_FOUND)

        subjects_serialized = SubjectSerializer(subjects, many=True)
        return Response(subjects_serialized.data, status=status.HTTP_200_OK)


class StudentClassView(ModelViewSet):
    queryset = StudentClass.objects.all()
    serializer_class = StudentClassSerializer
