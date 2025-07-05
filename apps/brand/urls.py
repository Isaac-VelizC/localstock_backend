from rest_framework.routers import DefaultRouter
from .views import BrandViewSet, UnitViewSet

router = DefaultRouter()
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'units', UnitViewSet, basename='unit')

urlpatterns = router.urls
