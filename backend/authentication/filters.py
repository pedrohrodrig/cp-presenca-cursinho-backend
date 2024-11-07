import django_filters

from django.db.models import Q

from .models import Roles, User

class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_by_all_fields')

    class Meta:
        model = User
        fields = {
            "role": ["exact", "in"],
        }

    def filter_by_all_fields(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(email__icontains=value)
        )