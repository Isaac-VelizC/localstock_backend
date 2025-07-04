from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WarehouseView

router = DefaultRouter()
router.register(r'warehouses', WarehouseView, basename='warehouse')
urlpatterns = [
    path('', include(router.urls)),
]
