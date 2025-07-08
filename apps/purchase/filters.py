import django_filters
from .models import Purchase

class PurchaseFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="purchase_date", lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name="purchase_date", lookup_expr='lte')

    class Meta:
        model = Purchase
        fields = ['status']
