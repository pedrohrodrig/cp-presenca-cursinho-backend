from django.urls import include, path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import LessonView, StudentView

urlpatterns = format_suffix_patterns(
    [
        path("lesson/", LessonView.as_view({"get": "list", "post": "create"})),
        path(
            "lesson/<int:pk>/",
            LessonView.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        ),
        path("student/", StudentView.as_view({"get": "list", "post": "create"})), 
        path("student/<int:pk>", StudentView.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}))
    ]
)

