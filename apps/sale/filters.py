from .models import Sale
import django_filters

class SaleFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="sale_date", lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name="sale_date", lookup_expr='lte')

    class Meta:
        model = Sale
        fields = ['status', 'payment_status']
