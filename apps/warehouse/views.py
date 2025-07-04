from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import WarehouseSerializer
from .models import Warehouse

class WarehouseView(viewsets.ModelViewSet):
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Retorna solo los almacenes no eliminados del store del usuario autenticado.
        """
        user = self.request.user
        return Warehouse.objects.filter(
            store=user.store,
            soft_delete=False  # Excluir eliminados lógicamente
        ).order_by('-created_at')

    def perform_destroy(self, instance):
        """
        Implementa el soft delete al eliminar un almacén.
        """
        instance.soft_delete = True
        instance.save()

    def paginate_queryset(self, queryset):
        """
        Permite desactivar la paginación pasando ?paginate=false
        """
        if self.request.query_params.get('paginate') == 'false':
            return None
        return super().paginate_queryset(queryset)

    def list(self, request, *args, **kwargs):
        """
        Lista almacenes filtrando y paginando según parámetros.
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='warehouse-search')
    def warehouse_search(self, request):
        search = request.query_params.get('search', '')
        user = request.user
        queryset = Warehouse.objects.filter(
                store=user.store,
                name__icontains=search,
                soft_delete=False,
                is_active=True
            ).only('id', 'name').order_by('name')
        return Response([{'id': u.id, 'name': u.name} for u in queryset])