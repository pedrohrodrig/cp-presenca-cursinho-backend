import django_filters

from .models import Lesson


class LessonFilter(django_filters.FilterSet):
    student_class = django_filters.CharFilter(field_name="lesson_recurrency__student_class", lookup_expr="name__exact")
    subject = django_filters.CharFilter(field_name="lesson_recurrency__subject", lookup_expr="name__exact")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    day = django_filters.NumberFilter(field_name="start_datetime", lookup_expr="day__exact")

    class Meta:
        model = Lesson
        fields = {
            "start_datetime": ["lte", "gte"],
        }
