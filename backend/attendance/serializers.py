from rest_framework import serializers

from .models import Attendance, Lesson, LessonRecurrency, LessonRecurrentDatetime, Student, StudentClass, Subject


class StudentClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClass
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    is_attendance_registrable = serializers.SerializerMethodField()

    def get_is_attendance_registrable(self, obj):
        return obj.is_attendance_registrable

    class Meta:
        model = Lesson
        exclude = ["is_manual_attendance_checked", "manual_attendance_last_time_edited"]


class LessonPasskeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["passkey"]  # Apenas o campo passkey


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            "status",
            "student",
            "lesson",
        ]


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"


class StudentClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClass
        fields = "__all__"


class LessonWithDetailsSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    student_class = serializers.SerializerMethodField()
    is_attendance_registrable = serializers.SerializerMethodField()

    def get_subject(self, obj):
        return obj.lesson_recurrency.subject.name

    def get_course(self, obj):
        return obj.lesson_recurrency.student_class.course

    def get_student_class(self, obj):
        return obj.lesson_recurrency.student_class.name

    def get_is_attendance_registrable(self, obj):
        return obj.is_attendance_registrable

    class Meta:
        model = Lesson
        fields = [
            "id",
            "name",
            "passkey",
            "start_datetime",
            "end_datetime",
            "attendance_start_datetime",
            "attendance_end_datetime",
            "is_attendance_registrable",
            "subject",
            "course",
            "student_class",
        ]


class LessonRecurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonRecurrency
        fields = "__all__"


class LessonRecurrentDatetimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonRecurrentDatetime
        fields = "__all__"


class LessonRecurrencyWithDatetimeSerializer(serializers.ModelSerializer):
    lesson_datetimes = serializers.SerializerMethodField()

    def get_lesson_datetimes(self, obj):
        datetimes = LessonRecurrentDatetime.objects.filter(lesson_recurrency=obj.id)
        datetimes_serialized = LessonRecurrentDatetimeSerializer(datetimes, many=True)

        return datetimes_serialized.data

    class Meta:
        model = LessonRecurrency
        fields = ["id", "student_class", "subject", "lesson_datetimes"]


class MobileLessonSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    student_class = serializers.SerializerMethodField()
    is_attendance_registrable = serializers.SerializerMethodField()

    def get_subject(self, obj):
        return obj.lesson_recurrency.subject.name

    def get_course(self, obj):
        return obj.lesson_recurrency.student_class.course

    def get_student_class(self, obj):
        return obj.lesson_recurrency.student_class.name

    def get_is_attendance_registrable(self, obj):
        return obj.is_attendance_registrable

    class Meta:
        model = Lesson
        fields = [
            "id",
            "name",
            "start_datetime",
            "end_datetime",
            "attendance_start_datetime",
            "attendance_end_datetime",
            "is_attendance_registrable",
            "subject",
            "course",
            "student_class",
        ]
