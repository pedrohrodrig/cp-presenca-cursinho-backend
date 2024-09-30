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
)

urlpatterns = format_suffix_patterns(
    [
        path("lesson/", LessonView.as_view({"get": "list", "post": "create"})),
        path(
            "lesson/<int:pk>/",
            LessonView.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        ),
        path("lesson/<int:pk>/update_passkey/", LessonView.as_view({"patch": "update_passkey"})),
        path(
            "lesson/<int:pk>/update_attendance_registrability/",
            AttendanceRegistrabilityView.as_view({"patch": "update_attendance_registrability"}),
        ),
        path("lesson_with_details/", LessonView.as_view({"get": "list_today_lessons_with_details"})),
        path("mobile_lesson_with_details/", LessonView.as_view({"get": "list_mobile_lessons_with_details"})),
        path("attendance/", AttendanceView.as_view({"post": "create"})),
        path("student/", StudentView.as_view({"get": "list", "post": "create"})),
        path(
            "student/<int:pk>/",
            StudentView.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        ),
        path("subject/", SubjectView.as_view({"get": "list", "post": "create_subject_and_recurrency"})),
        path(
            "subject/<int:pk>",
            SubjectView.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        ),
        path("student-class/", StudentClassView.as_view({"get": "list", "post": "create"})),
        path(
            "student-class/<int:pk>",
            StudentClassView.as_view(
                {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
            ),
        ),
        path(
            "subject/<str:main_subject>/",
            SubjectView.as_view({"get": "list_from_main_subject"}),
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
    ]
)
