from rest_framework import serializers

from .models import Attendance, StudentClass, Lesson, Subject, Student

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


class LessonWithDetailsSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    student_class = serializers.SerializerMethodField()

    def get_subject(self, obj):
        return obj.lesson_recurrency.subject.name
    
    def get_course(self, obj):
        return obj.lesson_recurrency.student_class.course
    
    def get_student_class(self, obj):
        return obj.lesson_recurrency.student_class.name

    class Meta:
        model = Lesson
        fields = ["id", "start_datetime", "end_datetime", "attendance_start_datetime", "attendance_end_datetime", "is_attendance_registrable", "subject", "course", "student_class"]