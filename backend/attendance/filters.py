import django_filters

from .models import Lesson


class LessonFilter(django_filters.FilterSet):
    student_class = django_filters.CharFilter(field_name="lesson_recurrency__student_class__name", lookup_expr="exact")

    class Meta:
        model = Lesson
        fields = []
