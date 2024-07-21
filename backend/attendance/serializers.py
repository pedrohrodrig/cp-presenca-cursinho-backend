from rest_framework import serializers

from .models import Attendance, Lesson, Student, StudentClass, Subject


class StudentClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClass
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class LessonPasskeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["is_attendance_registrable"]  # Apenas o campo passkey


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            "status",
            "student",
            "lesson_session",
        ]


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"
