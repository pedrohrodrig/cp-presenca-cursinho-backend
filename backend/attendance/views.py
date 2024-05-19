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
    def create(self, request): 
        serializer = StudentSerializer(data=request.data)
        if not serializer.is_valid(): 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        student = Student.objects.create(**serializer.validated_data)
        student_serialized = StudentSerializer(student)

        return Response(student_serialized.data, status=status.HTTP_201_CREATED)
    
    def list_all(self, request):
        student_list = Student.objects.all()

        if not student_list: 
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = StudentSerializer(student_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk):
        student = Student.objects.filter(pk=pk).first()

        if not student:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = StudentSerializer(student)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk): 
        queryset = Student.objects.filter(pk=pk).first()

        if not queryset: 
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        queryset.delete()
        serializer = StudentSerializer(queryset)

        return Response(serializer.data, status=status.HTTP_200_OK)
        
