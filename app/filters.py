import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='iexact')
    search = django_filters.filters.CharFilter(field_name='name', lookup_expr='icontains')
    minPrice = django_filters.filters.NumberFilter(field_name='price', lookup_expr='gte')
    maxPrice = django_filters.filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['price', 'name', 'category', 'search', 'minPrice', 'maxPrice']