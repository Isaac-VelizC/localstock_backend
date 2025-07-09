from rest_framework import viewsets, filters, status, serializers
from .serializers import SaleListSerializer, SaleDetailSerializer
from .utils import procesar_cancelacion, procesar_confirmacion
from django_filters.rest_framework import DjangoFilterBackend
from apps.warehouse.utils import get_default_warehouse
from rest_framework.permissions import IsAuthenticated
from .serializer_create import SaleCreateSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from .filters import SaleFilter
from .models import Sale

# Create your views here.
class SaleViewSet(viewsets.ModelViewSet):
    permission_classes = [ IsAuthenticated ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SaleFilter
    search_fields = ['invoice_number', 'customer__name', 'notes', 'sale_number']
    ordering_fields = ['invoice_number', 'customer__name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        warehouse = get_default_warehouse(user)
        return Sale.objects.filter(store=user.store, warehouse=warehouse).select_related('customer').prefetch_related('details__product')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SaleListSerializer
        elif self.action == 'retrieve':
            return SaleDetailSerializer
        elif self.action in  ['create', 'update', 'partial_update']:
            return SaleCreateSerializer
        return SaleDetailSerializer
    
    @action(detail=True, methods=['put'], url_path='confirm')
    def confirm(self, request, pk=None):
        user = request.user
        sale = self.get_object()
        try:
            procesar_confirmacion(sale, user)
            return Response({'detail': 'Venta confirmada con éxito.'})
        except serializers.ValidationError as e:
            return Response({'detail': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        user = request.user
        sale = self.get_object()
        try:
            procesar_cancelacion(sale, user)
            return Response({'detail': 'Venta cancelada con éxito.'}, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response({'detail': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
        elif instance.status == 'pending':
            return Response(
                {'detail': 'No se puede eliminar una compra pendiente.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(instance)
        return Response({'detail': 'Compra eliminada correctamente.'}, status=status.HTTP_204_NO_CONTENT)
