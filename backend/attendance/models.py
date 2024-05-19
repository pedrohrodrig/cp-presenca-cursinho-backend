from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Subject(models.Model):
    name = models.CharField(max_length=30, unique=True)


class Class(models.Model):
    name = models.CharField(max_length=30, unique=True)
    classroom = models.CharField(max_length=10, blank=True, null=True)
    course = models.CharField(max_length=10)  # TODO: criar modelo com ChoiceField
    subjects = models.ManyToManyField(Subject, related_name="classes")


class Student(models.Model):
    full_name = models.CharField(max_length=100, null=False, blank=False)
    course_class = models.OneToOneField(Class, on_delete=models.CASCADE, related_name="students")


class Lesson(models.Model):
    course_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="lessons")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="lessons")


class LessonDatetime(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="datetimes")
    datetime = models.DateTimeField()
    # TODO: conferir se diferentes aulas tem duração diferente


class Attendance(models.Model):
    class AttendanceChoices(models.TextChoices):
        PRESENT = "P", _("Present")
        ABSENT = "A", _("Absent")
        JUSTIFIED = "J", _("Justified")

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="attendances")
    datetime = models.DateTimeField(auto_now_add=True, blank=True)
    status = models.CharField(max_length=1, choices=AttendanceChoices, default=AttendanceChoices.ABSENT)

