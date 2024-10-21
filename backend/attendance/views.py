from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.test import RequestFactory
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from .filters import LessonFilter
from .models import Attendance, Lesson, LessonRecurrency, LessonRecurrentDatetime, Student, StudentClass, Subject
from .serializers import (
    AttendanceSerializer,
    LessonPasskeySerializer,
    LessonRecurrencySerializer,
    LessonRecurrencyWithDatetimeSerializer,
    LessonRecurrentDatetimeSerializer,
    LessonSerializer,
    LessonWithDetailsSerializer,
    MobileLessonSerializer,
    StudentClassSerializer,
    StudentSerializer,
    SubjectSerializer,
)

# Create your views here.


class LessonView(ModelViewSet):
    queryset = Lesson.objects.all().order_by("start_datetime")
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = LessonFilter

    def create_from_recurrency(self, recurrent_datetime):
        current_date = recurrent_datetime.start_datetime
        current_weekday = current_date.date().weekday()
        days = ((recurrent_datetime.day_of_week - current_weekday) + 7) % 7
        start_datetime = recurrent_datetime.start_datetime + timedelta(days=days)
        end_datetime = recurrent_datetime.end_datetime + timedelta(days=days)

        lessons_to_create = []

        for i in range(10):
            lesson_data = {
                "lesson_recurrency": recurrent_datetime.lesson_recurrency,
                "lesson_recurrent_datetime": recurrent_datetime,
                "name": f"Aula de {recurrent_datetime.lesson_recurrency.subject}",
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "attendance_start_datetime": start_datetime,
                "attendance_end_datetime": end_datetime,
            }

            lessons_to_create.append(Lesson(**lesson_data))
            start_datetime += timedelta(days=7)
            end_datetime += timedelta(days=7)

        Lesson.objects.bulk_create(lessons_to_create)
        lessons_serialized = LessonSerializer(lessons_to_create, many=True)

        return lessons_serialized.data

    def create_lesson_with_deatils(self, request):
        recurrency = LessonRecurrency.objects.get(
            subject__name=request.data["subject"], student_class__name=request.data["student_class"]
        )
        lesson_data = {**request.data, "lesson_recurrency": recurrency.id}

        serializer = LessonSerializer(data=lesson_data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        lesson = Lesson.objects.create(**serializer.validated_data)
        lesson_serialized = LessonSerializer(lesson)

        return Response(lesson_serialized.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk):
        lesson = Lesson.objects.filter(pk=pk).first()
        if not lesson:
            return Response(status=status.HTTP_404_NOT_FOUND)

        lesson_serialized = LessonWithDetailsSerializer(lesson)

        return Response(lesson_serialized.data, status=status.HTTP_200_OK)

    def list_lessons_with_details(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        lessons_list_serialized = LessonWithDetailsSerializer(queryset, many=True)

        return Response(lessons_list_serialized.data, status=status.HTTP_200_OK)

    def list_today_lessons_with_details(self, request):
        now = timezone.localtime(timezone.now())
        queryset = self.get_queryset().filter(start_datetime__day=now.day)
        queryset = self.filter_queryset(queryset)

        lessons_list_serialized = LessonWithDetailsSerializer(queryset, many=True)

        return Response(lessons_list_serialized.data, status=status.HTTP_200_OK)

    def list_mobile_lessons_with_details(self, request):
        queryset = Lesson.objects.all()

        lessons_list_serialized = MobileLessonSerializer(queryset, many=True)

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

    def checkPassKey(self, request):
        lesson_id = request.data.get("lesson_id")
        student_id = request.data.get("student_id")
        passkey = request.data.get("passkey")

        if not lesson_id or not passkey:
            return Response("Lesson ID and passkey are required", status=status.HTTP_400_BAD_REQUEST)

        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response("Lesson not found", status=status.HTTP_404_NOT_FOUND)

        if lesson.passkey != passkey:
            return Response("Invalid passkey", status=status.HTTP_403_FORBIDDEN)

        new_data = {"lesson": lesson_id, "student": student_id, "status": "P"}  # Define status como "P" (Present)

        serializer = AttendanceSerializer(data=new_data)

        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


class LessonRecurrencyView(ModelViewSet):
    queryset = LessonRecurrency.objects.all()
    serializer_class = LessonRecurrencySerializer

    def list_recurrency_with_datetime(self, request):
        queryset = LessonRecurrency.objects.all()
        recurrency_list_serialized = LessonRecurrencyWithDatetimeSerializer(queryset, many=True)

        return Response(recurrency_list_serialized.data, status=status.HTTP_200_OK)

    def list_recurrency_with_params(self, request, subject, student_class):
        recurrency = LessonRecurrency.objects.filter(subject=subject, student_class=student_class).first()

        if not recurrency:
            return Response(status=status.HTTP_404_NOT_FOUND)

        recurrency_serialized = LessonRecurrencyWithDatetimeSerializer(recurrency)
        return Response(recurrency_serialized.data, status=status.HTTP_200_OK)


class LessonRecurrentDatetimeView(ModelViewSet):
    queryset = LessonRecurrentDatetime.objects.all()
    serializer_class = LessonRecurrentDatetimeSerializer

    def create_datetime_with_lessons(self, request):
        serializer = LessonRecurrentDatetimeSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        recurrent_datetime = LessonRecurrentDatetime.objects.create(**serializer.validated_data)
        recurrent_datetime_serialized = LessonRecurrentDatetimeSerializer(recurrent_datetime)

        try:
            LessonView.create_from_recurrency(self, recurrent_datetime)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        return Response(recurrent_datetime_serialized.data, status=status.HTTP_201_CREATED)

    def update_datetime_with_lessons(self, request, pk):
        recurrent_datetime = LessonRecurrentDatetime.objects.get(pk=pk)
        # lessons = Lesson.objects.filter(lesson_recurrent_datetime=recurrent_datetime.id, start_datetime__gte=timezone.now())
        lessons = Lesson.objects.filter(lesson_recurrent_datetime=recurrent_datetime.id)
        lessons.delete()

        recurrent_datetime.start_datetime = datetime.fromisoformat(
            request.data.get("start_datetime", recurrent_datetime.start_datetime)[:-1] + "+00:00"
        )
        recurrent_datetime.end_datetime = datetime.fromisoformat(
            request.data.get("end_datetime", recurrent_datetime.start_datetime)[:-1] + "+00:00"
        )
        recurrent_datetime.day_of_week = int(request.data.get("day_of_week", recurrent_datetime.day_of_week))
        recurrent_datetime.save()

        try:
            LessonView.create_from_recurrency(self, recurrent_datetime)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        serializer = LessonRecurrentDatetimeSerializer(recurrent_datetime)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentClassView(ModelViewSet):
    queryset = StudentClass.objects.all().order_by("name")
    serializer_class = StudentClassSerializer
