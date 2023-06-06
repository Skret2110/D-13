"""
Файл создан для реализации фильтров, например поиска объектов в приложении
"""

from django_filters import FilterSet, DateFilter
from .models import Post



class PostFilter(FilterSet):
    time_of_creation = DateFilter

    class Meta:
        model = Post
        fields = {
            'post_category': ['exact'],
            'time_of_creation': ['gte'],
            'title': ['icontains'],
            'author': ['exact'],
        }
