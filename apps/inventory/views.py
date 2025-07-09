from rest_framework import viewsets, permissions, filters, views
from .serializers import InventoryTransactionSerializer
from apps.warehouse.utils import get_default_warehouse
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.timezone import timedelta, now
from rest_framework.response import Response
from .models import InventoryTransaction
from apps.product.models import Product
from django.db.models import Sum

# Create your views here.
class InventoryTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'created_at', 'product']
    search_fields = ['reason', 'reference_type', 'product__name', 'product__code']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        warehouse = get_default_warehouse(user)
        # Puedes filtrar por la tienda o almacén asociado al usuario si lo necesitas.
        return InventoryTransaction.objects.filter(store=user.store, warehouse=warehouse).order_by('-created_at')

class LowStockAlertView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        warehouse = get_default_warehouse(user)
        productos = Product.objects.filter(
            store=user.store,
            warehouse=warehouse,
            is_active=True,
            soft_deleted=False,
            stock__lte=5  # aquí puedes parametrizar el umbral de "bajo stock"
        ).values('id', 'name', 'stock')

        return Response({"low_stock_products": list(productos)})

class StockStatusSummaryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        warehouse = get_default_warehouse(user)
        productos = Product.objects.filter(
            store=user.store,
            warehouse=warehouse,
            is_active=True,
            soft_deleted=False,
        )

        ready = productos.filter(stock__gt=5).count()
        alert = productos.filter(stock__lte=5).count()

        return Response({
            "ready_to_sell": ready,
            "stock_alert": alert,
            "total": ready + alert
        })

class TopMostStockedProductsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        warehouse = get_default_warehouse(user)
        top_products = Product.objects.filter(
            store=user.store,
            warehouse=warehouse,
            is_active=True,
            soft_deleted=False
        ).order_by('-stock')[:10].values('id', 'name', 'stock')

        return Response({"top_most_stocked": list(top_products)})

class TopLeastStockedProductsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        warehouse = get_default_warehouse(user)
        bottom_products = Product.objects.filter(
            store=user.store,
            warehouse=warehouse,
            is_active=True,
            soft_deleted=False
        ).order_by('stock')[:10].values('id', 'name', 'stock')

        return Response({"top_least_stocked": list(bottom_products)})

class StockOverTimeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        warehouse = get_default_warehouse(user)

        days = 15  # cambiar por 30 o lo que necesites
        data = []

        for i in range(days):
            day = now().date() - timedelta(days=i)
            total_stock = InventoryTransaction.objects.filter(
                store=user.store,
                warehouse=warehouse,
                created_at__date__lte=day
            ).aggregate(stock=Sum('quantity'))['stock'] or 0

            data.append({
                "date": day.strftime('%Y-%m-%d'),
                "total_stock": total_stock
            })

        return Response({"stock_over_time": list(reversed(data))})
