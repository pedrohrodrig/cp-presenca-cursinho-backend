from django.contrib import admin

from .models import Attendance, Class, Lesson, LessonDatetime, Student, Subject

# Register your models here.
admin.site.register(Attendance)
admin.site.register(Class)
admin.site.register(Lesson)
admin.site.register(LessonDatetime)
admin.site.register(Subject)
admin.site.register(Student)
