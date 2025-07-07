from .serializers import SupplierSerializer, SupplierSelectSerializer
from rest_framework import permissions, viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Supplier

# Create your views here.
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country', 'is_active']
    search_fields = ['name', 'contact_name', 'email', 'phone', 'nit']
    ordering_fields = ['email', 'nit', 'country']
    ordering = ['name']

    def get_queryset(self):
        return Supplier.objects.filter(
            store=self.request.user.store,
            soft_deleted=False
        )
    
    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        supplier = Supplier.all_objects.filter(pk=pk, store=request.user.store).first()
        if supplier and supplier.soft_deleted:
            supplier.soft_deleted = False
            supplier.deleted_at = None
            supplier.save()
            return Response({'status': 'Proveedor restaurado'})
        return Response({'error': 'Proveedor no encontrado o no eliminado'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path='search-item')
    def search_item(self, request):
        search = request.query_params.get('search', '')
        user = request.user

        queryset = Supplier.objects.filter(
            store=user.store,
            soft_deleted=False,
            is_active=True
        ).filter(
            Q(name__icontains=search) | Q(nit__icontains=search)
        ).order_by('-created_at')

        serializer = SupplierSelectSerializer(queryset, many=True)
        return Response(serializer.data)