from rest_framework import serializers

from .models import Attendance, Class, Lesson, LessonSession, Subject


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class LessonSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonSession
        fields = "__all__"


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            "status",
            "student",
            "lesson_session",
        ]
