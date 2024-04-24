import django_filters
from .models import Suburbs


class SuburbsFilter(django_filters.FilterSet):
    class Meta:
        model = Suburbs
        fields = {
            'State': ['exact'],
            'Suburb': ['icontains'],
            'Postcode': ['exact'],
        }
