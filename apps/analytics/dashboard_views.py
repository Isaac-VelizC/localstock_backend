# dashboard_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Count, F
from apps.product.models import Product
from apps.sale.models import Sale, SaleDetail
from apps.customer.models import Customer
from django.utils.timezone import now

# Constante para definir stock mínimo
LOW_STOCK_THRESHOLD = 10

class CountProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Product.objects.filter(is_active=True, soft_deleted=False).count()
        return Response({'count_products': count})


class CountSalesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Sale.objects.filter(status='completed').count()
        return Response({'count_sales': count})


class CountCustomersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Customer.objects.count()
        return Response({'count_customers': count})


class TopSellingProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        top_n = int(request.query_params.get('top', 5))
        top_products = (
            SaleDetail.objects
            .values('product__id', 'product__name')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')[:top_n]
        )
        return Response({'top_selling_products': list(top_products)})


class LowStockProductsCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Product.objects.filter(stock__lt=LOW_STOCK_THRESHOLD, is_active=True).count()
        return Response({'low_stock_count': count})


class LowStockProductsAlertView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.filter(stock__lt=LOW_STOCK_THRESHOLD, is_active=True)
        data = [
            {
                'id': p.id,
                'name': p.name,
                'stock': p.stock,
                'category': p.category.name if p.category else None,
                'warehouse': p.warehouse.name if p.warehouse else None,
            }
            for p in products
        ]
        return Response({'low_stock_products': data})

# Total neto de ventas completadas
class TotalRevenueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total = Sale.objects.filter(status='completed').aggregate(total=Sum('net_total'))['total'] or 0
        return Response({'total_revenue': float(total)})

# Total de ventas por mes
class MonthlySalesSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = (
            Sale.objects.filter(status='completed')
            .annotate(month=TruncMonth('sale_date'))
            .values('month')
            .annotate(total=Sum('net_total'))
            .order_by('month')
        )
        return Response({'monthly_sales': list(data)})

# Ventas agurpadas por estado
class SalesByStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = (
            Sale.objects.values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )
        return Response({'sales_by_status': list(data)})

# Categorías más vendidas por cantidad
class TopCategoriesSoldView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = (
            SaleDetail.objects
            .values('product__category__id', 'product__category__name')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')
        )[:5]

        formatted = []
        for item in data:
            formatted.append({
                'category_id': item['product__category__id'],
                'category_name': item['product__category__name'] or 'Sin categoría',
                'total_quantity': item['total_quantity'],
            })

        return Response({'top_categories_sold': formatted})

# Produtos con stock en 0
class ProductsOutOfStockView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.filter(stock=0, is_active=True)
        data = [{'id': p.id, 'name': p.name, 'warehouse': p.warehouse.name} for p in products]
        return Response({'out_of_stock_products': data})

# Valor del inventario actual
class TotalStockValueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        value = Product.objects.filter(is_active=True).aggregate(
            total=Sum(F('stock') * F('purchase_price'))
        )['total'] or 0
        return Response({'total_stock_value': float(value)})

# Ventas generadas hoy
class SalesTodayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = now().date()
        total = Sale.objects.filter(sale_date=today, status='completed').aggregate(total=Sum('net_total'))['total'] or 0
        return Response({'sales_today': float(total)})

# Promedio de ingreso por venta
class AverageTicketSizeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        completed_sales = Sale.objects.filter(status='completed')
        total = completed_sales.aggregate(total=Sum('net_total'))['total'] or 0
        count = completed_sales.count()
        average = total / count if count > 0 else 0
        return Response({'average_ticket_size': float(average)})
