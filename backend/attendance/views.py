from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Lesson, Student
from .serializers import LessonSerializer, StudentSerializer
# Create your views here.

class LessonView(ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class StudentView(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
