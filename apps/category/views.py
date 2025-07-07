from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import CategorySerializer, CategoryParentsSerializer
from .models import Category

# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return Category.objects.filter(store=user.store).order_by('-name', '-created_at')

    @action(detail=False, methods=['get'], url_path='items-search')
    def items_search(self, request):
        search = request.query_params.get('search', '')
        user = request.user
        queryset = Category.objects.filter(
            store=user.store, is_active=True, name__icontains=search
        ).only('id', 'name').order_by('name')[:10]
        serializer = CategoryParentsSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.subcategories.exists():
            return Response(
                {"error": "No se puede eliminar una categoría que tiene subcategorías."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)