from django.urls import include, path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (
    AttendanceRegistrabilityView,
    AttendanceView,
    LessonRecurrencyView,
    LessonRecurrentDatetimeView,
    LessonView,
    StudentClassView,
    StudentView,
    SubjectView,
    lessons_attendance_percentage,
    students_total_attendance_percentage,
)

urlpatterns = format_suffix_patterns(
    [
        path("lesson/", LessonView.as_view({"get": "list", "post": "create_lesson_with_deatils"})),
        path(
            "lesson/<int:pk>/",
            LessonView.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        ),
        path("lesson/<int:pk>/update_passkey/", LessonView.as_view({"patch": "update_passkey"})),
        path(
            "lesson/<int:pk>/update_attendance_registrability/",
            AttendanceRegistrabilityView.as_view({"patch": "update_attendance_registrability"}),
        ),
        path("lesson_with_details/", LessonView.as_view({"get": "list_lessons_with_details"})),
        path(
            "mobile_lesson_with_details/<int:student_class_id>",
            LessonView.as_view({"get": "list_mobile_lessons_with_details"}),
        ),
        path("attendance/", AttendanceView.as_view({"post": "create"})),
        path("attendance/<int:student_id>", AttendanceView.as_view({"get": "list_student_attendance"})),
        path("attendance/check-passkey", AttendanceView.as_view({"post": "check_pass_key"})),
        path("student/", StudentView.as_view({"get": "list_students", "post": "create"})),
        path(
            "student/<int:pk>/",
            StudentView.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        ),
        path(
            "student/lesson_attendance/<int:lesson_id>/",
            StudentView.as_view({"get": "list_students_lesson_attendance"}),
        ),
        path(
            "student/mobile/<int:user_id>/",
            StudentView.as_view({"get": "get_student"}),
        ),
        path("subject/", SubjectView.as_view({"get": "list", "post": "create_subject_and_recurrency"})),
        path("subject_with_details/<int:student_class>", SubjectView.as_view({"get": "list_subject_with_details"})),
        path(
            "subject/<int:pk>/",
            SubjectView.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        ),
        path(
            "subject/<str:main_subject>/",
            SubjectView.as_view({"get": "list_from_main_subject"}),
        ),
        path("student-class/", StudentClassView.as_view({"get": "list", "post": "create"})),
        path(
            "student-class/<int:pk>/",
            StudentClassView.as_view(
                {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
            ),
        ),
        path(
            "lesson_recurrency/",
            LessonRecurrencyView.as_view({"get": "list_recurrency_with_datetime", "post": "create"}),
        ),
        path(
            "lesson_recurrency/<int:pk>/",
            LessonRecurrencyView.as_view(
                {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
            ),
        ),
        path(
            "lesson_recurrency/<int:subject>/<int:student_class>/",
            LessonRecurrencyView.as_view({"get": "list_recurrency_with_params"}),
        ),
        path(
            "lesson_recurrent_datetime/",
            LessonRecurrentDatetimeView.as_view({"get": "list", "post": "create_datetime_with_lessons"}),
        ),
        path(
            "lesson_recurrent_datetime/<int:pk>/",
            LessonRecurrentDatetimeView.as_view(
                {"get": "retrieve", "put": "update", "patch": "update_datetime_with_lessons", "delete": "destroy"}
            ),
        ),
        path("student_class/", StudentClassView.as_view({"get": "list", "post": "create"})),
        path(
            "student_class/<int:pk>/",
            StudentClassView.as_view(
                {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
            ),
        ),
        path("metrics/students-total-attendance/", students_total_attendance_percentage),
        path("metrics/lessons_attendance_percentage/", lessons_attendance_percentage),
    ]
)
