import django_filters
from django.db.models import Value
from django.db.models.functions import Concat

from .models import Lesson, Student


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


class StudentFilter(django_filters.FilterSet):
    student_class = django_filters.CharFilter(field_name="student_class", lookup_expr="name__exact")
    name = django_filters.CharFilter(method="filter_full_name")

    class Meta:
        model = Student
        fields = {}

    def filter_full_name(self, queryset, name, value):
        queryset = queryset.annotate(full_name=Concat("user__first_name", Value(" "), "user__last_name"))

        return queryset.filter(full_name__icontains=value)
