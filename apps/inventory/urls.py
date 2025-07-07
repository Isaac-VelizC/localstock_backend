from rest_framework.routers import DefaultRouter
from .views import InventoryTransactionViewSet, LowStockAlertView, StockOverTimeView, StockStatusSummaryView, TopLeastStockedProductsView, TopMostStockedProductsView
from django.urls import path, include

router = DefaultRouter()
router.register(r'inventory', InventoryTransactionViewSet, basename='inventory')

urlpatterns = [
    path('', include(router.urls)),
    path('inventory/alerts/low-stock/', LowStockAlertView.as_view()),
    path('inventory/alerts/ready-vs-alert/', StockStatusSummaryView.as_view()),
    path('inventory/top/most-stocked/', TopMostStockedProductsView.as_view()),
    path('inventory/top/least-stocked/', TopLeastStockedProductsView.as_view()),
    path('inventory/analytics/stock-over-time/', StockOverTimeView.as_view()),
]