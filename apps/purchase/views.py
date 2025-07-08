from rest_framework import viewsets, permissions, filters, status, serializers, views
from .serializers import PurchaseListSerializer, PurchaseDetailSerializer
from .utils import procesar_confirmacion, procesar_cancelacion
from django_filters.rest_framework import DjangoFilterBackend
from .serializer_create import PurchaseCreateSerializer
from apps.warehouse.utils import get_default_warehouse
from django.db.models.functions import TruncMonth
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Purchase, PurchaseDetail
from django.db.models import Sum, Count
from django.utils.timezone import now
from .filters import PurchaseFilter
from datetime import timedelta

# Create your views here.
class PurchaseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PurchaseFilter  # ✅ Esta es la forma correcta
    search_fields = ['invoice_number', 'supplier__name', 'total']
    ordering_fields = ['created_at', 'invoice_number', 'purchase_date', 'net_total']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        warehouse = get_default_warehouse(user)
        return Purchase.objects.filter(store=user.store, warehouse=warehouse).prefetch_related('details', 'supplier')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseListSerializer
        elif self.action == 'retrieve':
            return PurchaseDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PurchaseCreateSerializer
        return PurchaseDetailSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status == 'completed':
            return Response(
                {'detail': 'No se puede eliminar una compra ya confirmada.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif instance.status == 'canceled':
            return Response(
                {'detail': 'No se puede eliminar una compra cancelada.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(instance)
        return Response({'detail': 'Compra eliminada correctamente.'}, status=status.HTTP_204_NO_CONTENT)
        
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        user = request.user
        purchase = self.get_object()

        if purchase.status == 'canceled':
            return Response({'detail': 'La compra ya está cancelada.'}, status=status.HTTP_400_BAD_REQUEST)
        if purchase.status == 'pending':
            # Dependiendo de la lógica, podrías permitir cancelar sin reversar stock
            pass

        try:
            procesar_cancelacion(purchase, user)
            return Response({'detail': 'Compra cancelada con éxito.'}, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response({'detail': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Fallback para errores inesperados
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    @action(detail=True, methods=['put'], url_path='confirm')
    def confirm(self, request, pk=None):
        user = request.user
        purchase = self.get_object()

        if purchase.status == 'completed':
            return Response({'detail': 'La compra ya fue confirmada previamente.'}, status=status.HTTP_400_BAD_REQUEST)

        if purchase.status == 'canceled':
            return Response({'detail': 'No se puede confirmar una compra cancelada.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            procesar_confirmacion(purchase, user)
            return Response({'detail': 'Compra confirmada con éxito.'}, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response({'detail': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TopPurchasedProductsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        warehouse = get_default_warehouse(user)

        queryset = PurchaseDetail.objects.filter(
            purchase__store=user.store,
            purchase__warehouse=warehouse,
            purchase__status='completed'
        ).values('product__name').annotate(
            total_quantity=Sum('quantity')
        ).order_by('-total_quantity')[:10]

        return Response(queryset)

class MonthlyPurchasesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        warehouse = get_default_warehouse(user)
        start_date = now() - timedelta(days=180)

        queryset = Purchase.objects.filter(
            store=user.store,
            warehouse=warehouse,
            status='completed',
            purchase_date__gte=start_date
        ).annotate(
            month=TruncMonth('purchase_date')
        ).values('month').annotate(
            total=Sum('total')
        ).order_by('month')

        return Response(queryset)
    
class PurchaseStatusSummaryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        warehouse = get_default_warehouse(user)

        summary = Purchase.objects.filter(
            store=user.store,
            warehouse=warehouse
        ).values('status').annotate(
            count=Count('id'),
            total=Sum('total')
        ).order_by('status')

        return Response(summary)

class TotalBySupplierView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        warehouse = get_default_warehouse(user)

        data = Purchase.objects.filter(
            store=user.store,
            warehouse=warehouse,
            status='completed'
        ).values('supplier__name').annotate(
            total_spent=Sum('total')
        ).order_by('-total_spent')[:10]

        return Response(data)
