import django_filters

from .models import Posts, Suburbs


class SuburbsFilter(django_filters.FilterSet):
    class Meta:
        model = Suburbs
        fields = {
            'State': ['exact'],
            'Suburb': ['icontains'],
            'Postcode': ['exact'],
        }


class PostsFilter(django_filters.FilterSet):
    type = django_filters.ChoiceFilter(
        field_name='type', choices=[(key, value) for key, value in Posts.TYPE_POST_CHOICE.items()], empty_label='All type')

    class Meta:
        model = Posts
        fields = {
            'hashtag': ['exact', 'contains'],
            'type': ['exact']
        }
