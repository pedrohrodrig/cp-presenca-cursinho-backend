from rest_framework import serializers

from .models import StudentClass, Lesson, Subject, Student

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

class StudentSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Student 
        fields = "__all__"