from .serializers import ProductCreateSerializer, ProductSerializer, ProductListSerializer, ProductSearchSelectSerializer, ProductBarcodeSerializer, ProductUpdateSerializer
from rest_framework import permissions, filters, serializers, status
from apps.warehouse.utils import get_default_warehouse
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product

# Create your views here.
class ProductViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug', 'code', 'barcode', 'description', 'brand__name', 'category__name', 'code']
    ordering_fields = ['name', 'created_at', 'sale_price', 'category__name']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        warehouse = get_default_warehouse(user)

        queryset = Product.objects.filter(
            store=user.store,
            warehouse=warehouse,
            soft_deleted=False
        ).select_related('brand', 'category', 'unit').prefetch_related('images')

        return self.apply_filters(queryset)
    
    def get_object(self):
        # Para restore queremos incluir los soft_deleted
        if self.action == 'restore':
            return Product.objects.filter(store=self.request.user.store).get(pk=self.kwargs['pk'])
        return super().get_object()
    
    def apply_filters(self, queryset):
        request = self.request
        # Filtro por categoría
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        # Filtro por precio
        price_range = request.query_params.get('price')
        if price_range:
            try:
                if '-' in price_range:
                    min_price, max_price = map(float, price_range.split('-'))
                    queryset = queryset.filter(sale_price__gte=min_price, sale_price__lte=max_price)
                elif price_range.endswith('+'):
                    min_price = float(price_range.replace('+', ''))
                    queryset = queryset.filter(sale_price__gte=min_price)
                else:
                    raise ValueError
            except (ValueError, TypeError):
                raise serializers.ValidationError("El rango de precio no es válido. Usa el formato '100-200' o '300+'.")

        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductSerializer
        elif self.action == 'create':
            return ProductCreateSerializer    
        elif self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        return ProductSerializer
    
    @action(detail=False, methods=['get'], url_path='search-item')
    def search_item(self, request):
        search = request.query_params.get('search', '')
        user = request.user
        warehouse = get_default_warehouse(user)

        queryset = Product.objects.filter(
            store=user.store,
            warehouse=warehouse,
            name__icontains=search,
            soft_deleted=False,
            is_active=True
        ).only('id', 'name').order_by('name')[:5]

        serializer = ProductSearchSelectSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # Busqueda por Codigo de barras
    @action(detail=False, methods=['get'], url_path='by-barcode')
    def by_barcode(self, request):
        barcode = request.query_params.get('barcode', '').strip()
        user = request.user
        warehouse = get_default_warehouse(user)

        if not barcode:
            return Response({"detail": "El parámetro 'barcode' es requerido."}, status=400)

        try:
            product = Product.objects.get(
                store=user.store,
                warehouse=warehouse,
                barcode=barcode,
                soft_deleted=False,
                is_active=True
            )
        except Product.DoesNotExist:
            return Response({"detail": "Producto no encontrado."}, status=404)

        serializer = ProductBarcodeSerializer(product)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        product = self.get_object()
        product.delete()  # llamamos al método del modelo
        return Response({"detail": "Producto marcado como eliminado (soft delete)."}, status=status.HTTP_200_OK)