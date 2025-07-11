from .serializers import CustomerSerializer, CustomerSelectSerializer
from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from apps.warehouse.utils import get_default_warehouse
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Customer

# Create your views here.
class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'surnames', 'email', 'phone', 'ci']
    ordering_fields = ['surnames', 'ci']
    ordering = ['name']
    
    def get_queryset(self):
        user = self.request.user
        warehouse = get_default_warehouse(user)
        
        return Customer.objects.filter(
            store=user.store,
            warehouse=warehouse,
            soft_deleted=False
        )
    
    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        customer = Customer.all_objects.filter(pk=pk, store=request.user.store).first()
        if customer and customer.soft_deleted:
            customer.soft_deleted=False
            customer.deleted_at=None
            customer.save()
            return Response({'status': 'Cliente restaurado'})
        return Response({'error': 'Cliente no encontrado o no eliminado'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path='search-item')
    def search_item(self, request):
        search = request.query_params.get('search', '')
        user = request.user
        warehouse = get_default_warehouse(user)
        queryset = Customer.objects.filter(
            store=user.store,
            warehouse=warehouse,
            soft_deleted=False,
            is_active=True
        ).filter(
            Q(name__icontains=search) | Q(surnames__icontains=search) | Q(ci__icontains=search)
        ).order_by('-created_at')
        
        serializer = CustomerSelectSerializer(queryset, many=True)
        return Response(serializer.data)
    