from rest_framework.routers import DefaultRouter
from .views import PurchaseViewSet, TopPurchasedProductsView, MonthlyPurchasesView, TotalBySupplierView, PurchaseStatusSummaryView
from django.urls import path, include

router = DefaultRouter()
router.register(r'purchases', PurchaseViewSet, basename='purchase')

urlpatterns = [
    path('', include(router.urls)),
    path('reports/top-products/', TopPurchasedProductsView.as_view()),
    # path('reports/low-products/', LeastPurchasedProductsView.as_view()),
    path('reports/monthly-purchases/', MonthlyPurchasesView.as_view()),
    path('reports/status-summary/', PurchaseStatusSummaryView.as_view()),
    path('reports/supplier-totals/', TotalBySupplierView.as_view()),
]