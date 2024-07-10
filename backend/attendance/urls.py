from django.urls import include, path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import AttendanceRegistrabilityView, AttendanceView, LessonView, StudentView

urlpatterns = format_suffix_patterns(
    [
        path("lesson/", LessonView.as_view({"get": "list", "post": "create"})),
        path(
            "lesson/<int:pk>/",
            LessonView.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        ),
        path(
            "lesson/<int:pk>/update_attendance_registrability/",
            AttendanceRegistrabilityView.as_view({"patch": "update_attendance_registrability"}),
        ),
        path("attendance/", AttendanceView.as_view({"post": "create"})),
        path("student/", StudentView.as_view({"get": "list", "post": "create"})), 
        path("student/<int:pk>", StudentView.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}))
    ]
)

