from django.urls import include, path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import AttendanceRegistrabilityView, AttendanceView, LessonView, StudentClassView, StudentView, SubjectView

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
        path("lesson_with_details/", LessonView.as_view({"get": "list_next_lessons_with_details"})),
        path("attendance/", AttendanceView.as_view({"post": "create"})),
        path("student/", StudentView.as_view({"get": "list", "post": "create"})),
        path(
            "student/<int:pk>/",
            StudentView.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        ),
        path("subject/", SubjectView.as_view({"get": "list", "post": "create_subject_and_recurrency"})),
        path(
            "subject/<int:pk>/",
            SubjectView.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        ),
        path(
            "subject/<str:main_subject>/",
            SubjectView.as_view({"get": "list_from_main_subject"}),
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
