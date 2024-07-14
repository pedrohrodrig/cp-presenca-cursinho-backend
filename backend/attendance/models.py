from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Subject(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class StudentClass(models.Model):
    name = models.CharField(max_length=30, unique=True)
    classroom = models.CharField(max_length=10, blank=True, null=True)
    course = models.CharField(max_length=100)  # TODO: criar modelo com ChoiceField
    subjects = models.ManyToManyField(Subject, related_name="student_classes")

    def __str__(self):
        return f"{self.name} - {self.course}"


class Student(models.Model):
    full_name = models.CharField(max_length=100, null=False, blank=False)
    course_class = models.OneToOneField(StudentClass, on_delete=models.CASCADE, related_name="students")

    def __str__(self):
        return self.full_name


class LessonRecurrency(models.Model):
    course_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name="lesson_recurrences")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="lesson_recurrences")


class LessonRecurrentDatetime(models.Model):
    lesson_recurrency = models.ForeignKey(LessonRecurrency, on_delete=models.CASCADE, related_name="regular_datetimes")
    datetime = models.DateTimeField()

    @property
    def day_of_week(self):
        # 0 = monday / 6 = sunday
        return self.datetime.weekday()


class Lesson(models.Model):
    lesson_recurrency = models.ForeignKey(LessonRecurrency, on_delete=models.CASCADE, related_name="lessons")
    name = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    attendance_start_datetime = models.DateTimeField()
    attendance_end_datetime = models.DateTimeField()
    is_attendance_registrable = models.BooleanField(blank=True, null=True, default=False)
    passkey = models.CharField(max_length=10, null=False, blank=False, default="1234567890")

    def __str__(self):
        return f"{self.lesson} - {self.time}"


class Attendance(models.Model):
    class AttendanceChoices(models.TextChoices):
        PRESENT = "P", _("Present")
        ABSENT = "A", _("Absent")
        JUSTIFIED = "J", _("Justified")

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="attendances")
    register_datetime = models.DateTimeField(auto_now_add=True, blank=True)
    status = models.CharField(max_length=1, choices=AttendanceChoices, default=AttendanceChoices.ABSENT)

    def __str__(self):
        return f"{self.student} - {self.lesson_session.lesson.subject.name}/{self.lesson_session.time} - {self.status}"
