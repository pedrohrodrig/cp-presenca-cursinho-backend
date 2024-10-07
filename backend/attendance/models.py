from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Subject(models.Model):
    class MainSubjectChoices(models.TextChoices):
        MATHEMATICS = (
            "MT",
            _("Matematica"),
        )
        PORTUGUESE = (
            "PT",
            _("Portugues"),
        )
        PHYSICS = (
            "PH",
            _("Fisica"),
        )
        CHEMISTRY = (
            "CH",
            _("Quimica"),
        )
        BIOLOGY = (
            "BI",
            _("Biologia"),
        )
        HISTORY = (
            "HI",
            _("Historia"),
        )
        GEOGRAPHY = (
            "GE",
            _("Geografia"),
        )
        PHILOSOPHY = (
            "PL",
            _("Filosofia"),
        )
        CURRENTAFFAIRS = "CA", ("Atualidades")

    name = models.CharField(max_length=30, unique=True)
    main_subject = models.CharField(max_length=2, choices=MainSubjectChoices, default=MainSubjectChoices.PORTUGUESE)

    def __str__(self):
        return self.name


class StudentClass(models.Model):
    class ModalityChoices(models.TextChoices):
        ONLINE = (
            "ON",
            _("Online"),
        )
        INCLASS = (
            "IN",
            _("Presencial"),
        )

    name = models.CharField(max_length=30, unique=True)
    classroom = models.CharField(max_length=10, blank=True, null=True)
    course = models.CharField(max_length=100)
    modality = models.CharField(max_length=2, choices=ModalityChoices, default=ModalityChoices.INCLASS)
    subjects = models.ManyToManyField(Subject, related_name="student_classes")

    def __str__(self):
        return f"{self.name} - {self.course}"


class Student(models.Model):
    full_name = models.CharField(max_length=100, null=False, blank=False)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name="students")

    def __str__(self):
        return self.full_name


class LessonRecurrency(models.Model):
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name="lesson_recurrences")
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
    passkey = models.CharField(max_length=10, null=False, blank=False, default="1234567890")
    is_manual_attendance_checked = models.BooleanField(blank=True, null=True, default=False)
    manual_attendance_last_time_edited = models.DateTimeField(null=True, blank=True)

    @property
    def is_attendance_registrable(self):
        if not self.manual_attendance_last_time_edited:
            return self.attendance_start_datetime <= timezone.now() <= self.attendance_end_datetime

        if (
            self.manual_attendance_last_time_edited < self.attendance_start_datetime
            or self.manual_attendance_last_time_edited > self.attendance_end_datetime
        ):
            return self.is_manual_attendance_checked

        manual_change_in_attendance_automated_period = (
            self.attendance_start_datetime <= self.manual_attendance_last_time_edited <= self.attendance_end_datetime
        )

        if manual_change_in_attendance_automated_period and not self.is_manual_attendance_checked:
            return False

        return self.attendance_start_datetime <= timezone.now() <= self.attendance_end_datetime

    def __str__(self):
        return f"{self.lesson_recurrency} - {self.start_datetime}"


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
        return f"{self.student} - {self.lesson.lesson_recurrency.subject.name}/{self.lesson.start_datetime} - {self.status}"
