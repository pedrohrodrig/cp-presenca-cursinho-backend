from django.urls import include, path
from rest_framework import routers

from .views import LessonView

router = routers.DefaultRouter()
router.register(r'lesson', LessonView)

urlpatterns = [
    path("", include(router.urls)),
]