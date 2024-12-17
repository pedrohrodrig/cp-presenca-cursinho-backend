from collections import defaultdict
from datetime import timedelta

from django.db.models import Count, F, Func
from django.db.models.functions import TruncDay, TruncHour, TruncWeek
from django.utils.timezone import localtime, now

from .models import Attendance, Lesson, Student, StudentClass, Subject

"""
Returns the total attendance percentage of the Students considering all the Lessons of all Subjects.
Can return total attendance percentage of a specific student if student_id is given. Can also return
total attendance percentage considering only Lessons of a specific Subject, if subject_id is given, or
total attendance percentage only of the Students of a centain StudentClass, if student_class_id is given.
"""


def get_students_total_attendance_percentage(student_id=None, student_class_id=None, subject_id=None):
    students_id = [student_id] if student_id else Student.objects.all().values_list("id", flat=True)
    student_classes_id = (
        [student_class_id] if student_class_id else StudentClass.objects.all().values_list("id", flat=True)
    )
    subjects_id = [subject_id] if subject_id else Subject.objects.all().values_list("id", flat=True)

    attendance_per_student = (
        Attendance.objects.filter(
            status=Attendance.AttendanceChoices.PRESENT,
            student__id__in=students_id,
            student__student_class__id__in=student_classes_id,
            lesson__lesson_recurrency__subject__id__in=subjects_id,
        )
        .values("student__id", student_class_id=F("student__student_class__id"))
        .annotate(total_attended=Count("id"))
    )

    if student_id:
        lessons_per_class = (
            Lesson.objects.filter(
                lesson_recurrency__student_class__students__id__contains=student_id,
                lesson_recurrency__student_class__id__in=student_classes_id,
                lesson_recurrency__subject__id__in=subjects_id,
            )
            .values(student_class_id=F("lesson_recurrency__student_class__id"))
            .annotate(total_lessons=Count("id"))
        )

    else:
        lessons_per_class = (
            Lesson.objects.filter(
                lesson_recurrency__student_class__id__in=student_classes_id,
                lesson_recurrency__subject__id__in=subjects_id,
            )
            .values(student_class_id=F("lesson_recurrency__student_class__id"))
            .annotate(total_lessons=Count("id"))
        )

    students_total_attendance_percentage = []
    for att in attendance_per_student:
        class_id = att["student_class_id"]
        std_id = att["student__id"]
        attended_lessons = att["total_attended"]

        total_lessons = next(
            (total["total_lessons"] for total in lessons_per_class if total["student_class_id"] == class_id), 0
        )

        attendance_percentage = (attended_lessons / total_lessons * 100) if total_lessons > 0 else 0
        students_total_attendance_percentage.append(
            {
                "student_id": std_id,
                "student": f"{Student.objects.get(id=std_id).user.first_name} {Student.objects.get(id=std_id).user.last_name}",
                "class_id": class_id,
                "subject_id": subject_id,
                "percentage_attendance": attendance_percentage,
            }
        )

    return students_total_attendance_percentage


"""
Returns the percentage of Students that attended each and all Lessons. Can return the attendance
percentage of a specific Lesson if lesson_id id given. If student_class_id or subject_id is given,
returns the percentage of Students that attended only the Lessons of that Subject or StudentClass.
"""


def get_lessons_attendance_percentage(lesson_id=None, student_class_id=None, subject_id=None):
    lessons_id = [lesson_id] if lesson_id else Lesson.objects.all().values_list("id", flat=True)
    student_classes_id = (
        [student_class_id] if student_class_id else StudentClass.objects.all().values_list("id", flat=True)
    )
    subjects_id = [subject_id] if subject_id else Subject.objects.all().values_list("id", flat=True)

    total_students_per_lesson = (
        Lesson.objects.filter(
            id__in=lessons_id,
            lesson_recurrency__student_class__id__in=student_classes_id,
            lesson_recurrency__subject__id__in=subjects_id,
        )
        .values(
            lesson_id=F("id"),
            subject_id=F("lesson_recurrency__subject__id"),
            student_class_id=F("lesson_recurrency__student_class__id"),
        )
        .annotate(total_students=Count("lesson_recurrency__student_class__students"))
    )

    present_students_per_lesson = (
        Attendance.objects.filter(
            lesson__id__in=lessons_id,
            lesson__lesson_recurrency__student_class__id__in=student_classes_id,
            lesson__lesson_recurrency__subject__id__in=subjects_id,
            status=Attendance.AttendanceChoices.PRESENT,
        )
        .values(les_id=F("lesson__id"))
        .annotate(
            present_students=Count("student"),
        )
    )

    lesson_attendance_percentage = []
    for lesson in total_students_per_lesson:
        les_id = lesson["lesson_id"]
        std_class_id = lesson["student_class_id"]
        subj_id = lesson["subject_id"]
        total_students = lesson["total_students"]

        present_students = next(
            (att["present_students"] for att in present_students_per_lesson if att["les_id"] == les_id), 0
        )

        attendance_percentage = (present_students / total_students) * 100 if total_students > 0 else 0
        lesson_attendance_percentage.append(
            {
                "lesson_id": les_id,
                "student_class_id": std_class_id,
                "subject_id": subj_id,
                "attendance_percentage": attendance_percentage,
            }
        )

    return lesson_attendance_percentage


"""
Returns all Lessons of a Student with a binary 'attended' column that holds 1 if the
Student attended the Lesson and 0 otherwise.
"""


def get_student_lesson_attendance(student_id, subject_id=None):
    subjects_id = [subject_id] if subject_id else Subject.objects.all().values_list("id", flat=True)

    lessons_of_student = Lesson.objects.filter(
        lesson_recurrency__student_class__students__id__contains=student_id,
        lesson_recurrency__subject__id__in=student_id,
    ).values(lesson_id=F("id"), subject_id=F("lesson_recurrency__subject__id"))

    attended_of_student = Attendance.objects.filter(
        student__id=student_id,
        lesson__lesson_recurrency__subject__id__in=subjects_id,
        status=Attendance.AttendanceChoices.PRESENT,
    ).values_list("lesson__id", flat=True)

    attended_lesson_ids = set(attended_of_student)

    student_lesson_attendance = []
    for lesson in lessons_of_student:
        subj_id = lesson["subject_id"]
        lesson_id = lesson["lesson_id"]

        attended = 1 if lesson_id in attended_lesson_ids else 0

        student_lesson_attendance.append(
            {
                "student_id": student_id,
                "subject_id": subj_id,
                "lesson_id": lesson_id,
                "attended": attended,
            }
        )

    return student_lesson_attendance


"""
Returns the average attendance of each Subject accross all Lessons and StudentClasses.
Can return the average attendance of a specific Subject if subject_id is given and the
average attendance accross Lessons of a specific StudentClass if student_class_id is given.
"""


def get_subjects_avg_attendance_percentage(student_class_id=None, subject_id=None):
    subjects_id = [subject_id] if subject_id else Subject.objects.all().values_list("id", flat=True)
    student_classes_id = (
        [student_class_id] if student_class_id else StudentClass.objects.all().values_list("id", flat=True)
    )

    lesson_attendance_percentage = get_lessons_attendance_percentage(
        student_class_id=student_class_id, subject_id=subject_id
    )

    subject_totals = defaultdict(lambda: {"total_percentage": 0, "lesson_count": 0})

    for lesson in lesson_attendance_percentage:
        subj_id = lesson["subject_id"]
        attendance_percentage = lesson["attendance_percentage"]

        subject_totals[subj_id]["total_percentage"] += attendance_percentage
        subject_totals[subj_id]["lesson_count"] += 1

    for subj_id in Subject.objects.filter(id__in=subjects_id, student_classes__id__in=student_classes_id).values_list(
        "id", flat=True
    ):
        if subj_id not in subject_totals:
            subject_totals[subj_id]["total_percentage"] = 0
            subject_totals[subj_id]["lesson_count"] = 0

    subject_avg_attendance_percentage = [
        {
            "subject_id": subj_id,
            "subject": Subject.objects.get(id=subj_id).name,
            "average_attendance_percentage": (totals["total_percentage"] / totals["lesson_count"])
            if totals["lesson_count"] > 0
            else 0,
        }
        for subj_id, totals in subject_totals.items()
    ]

    return subject_avg_attendance_percentage


"""
Returns the average attendance of each Student Class accross all Lessons and Subjects.
Can return the average attendance of a specific Class if student_class_id is given and the
average attendance accross Lessons of a specific Subject if subject_id is given.
"""


def get_student_classes_avg_attendance_percentage(student_class_id=None, subject_id=None):
    subjects_id = [subject_id] if subject_id else Subject.objects.all().values_list("id", flat=True)
    student_classes_id = (
        [student_class_id] if student_class_id else StudentClass.objects.all().values_list("id", flat=True)
    )

    lesson_attendance_percentage = get_lessons_attendance_percentage(
        student_class_id=student_class_id, subject_id=subject_id
    )

    student_class_totals = defaultdict(lambda: {"total_percentage": 0, "lesson_count": 0})

    for lesson in lesson_attendance_percentage:
        st_class_id = lesson["student_class_id"]
        attendance_percentage = lesson["attendance_percentage"]

        student_class_totals[st_class_id]["total_percentage"] += attendance_percentage
        student_class_totals[st_class_id]["lesson_count"] += 1

    for st_class_id in StudentClass.objects.filter(id__in=student_classes_id, subjects__id__in=subjects_id).values_list(
        "id", flat=True
    ):
        if st_class_id not in student_class_totals:
            student_class_totals[st_class_id]["total_percentage"] = 0
            student_class_totals[st_class_id]["lesson_count"] = 0

    student_class_avg_attendance_percentage = [
        {
            "student_class_id": st_class_id,
            "student_class": StudentClass.objects.get(id=st_class_id).name,
            "average_attendance_percentage": (totals["total_percentage"] / totals["lesson_count"])
            if totals["lesson_count"] > 0
            else 0,
        }
        for st_class_id, totals in student_class_totals.items()
    ]

    return student_class_avg_attendance_percentage


"""
Returns the attendance percentage of a Student in each Subject or in a specific
Subject if subject_id parameter is given.
"""


def get_student_attendance_percentage_per_subject(student_id, subject_id=None):
    subjects_id = [subject_id] if subject_id else Subject.objects.all().values_list("id", flat=True)

    lessons_per_subject = (
        Lesson.objects.filter(
            lesson_recurrency__student_class__students__id__contains=student_id,
            lesson_recurrency__subject__id__in=subjects_id,
        )
        .values(subject_id=F("lesson_recurrency__subject__id"))
        .annotate(total_lessons=Count("id"))
    )

    attended_per_subject = (
        Attendance.objects.filter(
            student__id=student_id,
            lesson__lesson_recurrency__subject__id__in=subjects_id,
            status=Attendance.AttendanceChoices.PRESENT,
        )
        .values(subject_id=F("lesson__lesson_recurrency__subject__id"))
        .annotate(attended_lessons=Count("id"))
    )

    student_attendance_percentage_per_subject = []
    for subj in lessons_per_subject:
        subj_id = subj["subject_id"]
        total_lessons = subj["total_lessons"]

        attended_lessons = next(
            (att["attended_lessons"] for att in attended_per_subject if att["subject_id"] == subj_id), 0
        )

        attendance_percentage = (attended_lessons / total_lessons * 100) if total_lessons > 0 else 0
        student_attendance_percentage_per_subject.append(
            {
                "student_id": student_id,
                "subject_id": subj_id,
                "attendance_percentage": attendance_percentage,
            }
        )

    return student_attendance_percentage_per_subject


"""
Returns the attendance history considering all students, subjects or classes. Can be divided in hours, days or weeks.
Can return the history of a specific student, class or subject if student_id, student_class_id or subject_id is given.
"""


def get_attendance_history(timespan="month", student_id=None, student_class_id=None, subject_id=None):
    students_id = [student_id] if student_id else Student.objects.all().values_list("id", flat=True)
    student_classes_id = (
        [student_class_id] if student_class_id else StudentClass.objects.all().values_list("id", flat=True)
    )
    subjects_id = [subject_id] if subject_id else Subject.objects.all().values_list("id", flat=True)

    current_time = localtime(now())
    if timespan == "day":
        start_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        group_by = TruncHour("register_datetime")  # Group by hour
    elif timespan == "month":
        start_time = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_time = (start_time + timedelta(days=32)).replace(day=1)  # First day of next month
        group_by = TruncDay("register_datetime")  # Group by day
    elif timespan == "year":
        start_time = current_time.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time.replace(year=start_time.year + 1)  # First day of next year
        group_by = TruncWeek("register_datetime")  # Group by week
    else:
        timespan = "month"
        start_time = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_time = (start_time + timedelta(days=32)).replace(day=1)  # First day of next month
        group_by = TruncDay("register_datetime")  # Group by day

    attendance_filter = Attendance.objects.filter(
        status=Attendance.AttendanceChoices.PRESENT,
        register_datetime__range=(start_time, end_time),
        student__id__in=students_id,
        student__student_class__id__in=student_classes_id,
        lesson__lesson_recurrency__subject__id__in=subjects_id,
    )

    grouping_fields = ["time_period"]
    if (not student_id and not student_class_id and subject_id) or (
        not student_id and not student_class_id and not subject_id
    ):
        grouping_fields.append("student_class_id")
    elif not student_id and not subject_id and student_class_id:
        grouping_fields.append("subject_id")

    attendance_groups = (
        attendance_filter.annotate(
            time_period=group_by,
            student_class_id=F("student__student_class__id"),
            subject_id=F("lesson__lesson_recurrency__subject__id"),
        )
        .values(*grouping_fields)
        .annotate(total_attendance=Count("id"))
        .order_by("time_period")
    )

    # Format the results
    attendance_history = []
    for group in attendance_groups:
        result = {
            "time_period": group["time_period"],
            "timespan": timespan,
            "total_attendance": group["total_attendance"],
        }
        if "student_class_id" in group:
            result["student_class_id"] = group["student_class_id"]
            result["student_class"] = StudentClass.objects.get(id=group["student_class_id"]).name
        if "subject_id" in group:
            result["subject_id"] = group["subject_id"]
            result["subject"] = Subject.objects.get(id=group["subject_id"]).name
        attendance_history.append(result)

    return attendance_history
