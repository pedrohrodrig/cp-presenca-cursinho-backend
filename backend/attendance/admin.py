from django.contrib import admin

from .models import Attendance, StudentClass, Lesson, LessonRecurrency, Student, Subject

# Register your models here.
admin.site.register(Attendance)
admin.site.register(StudentClass)
admin.site.register(Lesson)
admin.site.register(LessonRecurrency)
admin.site.register(Subject)
admin.site.register(Student)
