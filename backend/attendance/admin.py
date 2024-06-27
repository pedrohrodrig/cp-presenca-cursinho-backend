from django.contrib import admin

from .models import Attendance, Class, Lesson, LessonSession, Student, Subject

# Register your models here.
admin.site.register(Attendance)
admin.site.register(Class)
admin.site.register(Lesson)
admin.site.register(LessonSession)
admin.site.register(Subject)
admin.site.register(Student)
