from rest_framework import viewsets, permissions, serializers, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import BrandSerializer, UnitSerializer, BrandSearchSelectSerializer, UniSearchSelectSerializer
from .models import Brand, Unit

# Create your views here.
class BrandViewSet(viewsets.ModelViewSet):
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        return Brand.objects.filter(store=user.store).order_by('-created_at')
    
    def perform_create(self, serializer):
        user_store = getattr(self.request.user, 'store', None)
        if not user_store:
            raise serializers.ValidationError("El usuario no tiene una tienda asignada.")
        serializer.save(store=user_store)

    @action(detail=False, methods=['get'], url_path='brand-list')
    def brand_list(self, request):
        search = request.query_params.get('search', '')
        user = request.user
        queryset = Brand.objects.filter(
            store=user.store, is_active=True, name__icontains=search
        ).only('id', 'name').order_by('name')
        serializer = BrandSearchSelectSerializer(queryset, many=True)
        return Response(serializer.data)

class UnitViewSet(viewsets.ModelViewSet):
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Unit.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['created_at', 'name']
    ordering = ['name']

    def paginate_queryset(self, queryset):
        if self.request.query_params.get('paginate') == 'false':
            return None
        return super().paginate_queryset(queryset)

    @action(detail=False, methods=['get'], url_path='unit-search')
    def unit_search(self, request):
        search = request.query_params.get('search', '')
        queryset = Unit.objects.filter(name__icontains=search).only('id', 'name').order_by('name')
        serializer = UniSearchSelectSerializer(queryset, many=True)
        return Response(serializer.data)
