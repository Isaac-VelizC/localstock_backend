from django.urls import path
from .dashboard_views import (
    CountProductsView, CountSalesView, CountCustomersView,
    TopSellingProductsView, LowStockProductsCountView,
    LowStockProductsAlertView, TotalRevenueView, MonthlySalesSummaryView,
    SalesByStatusView, TopCategoriesSoldView,
    ProductsOutOfStockView, TotalStockValueView, SalesTodayView,
    AverageTicketSizeView
)

urlpatterns = [
    path('dashboard/count-products/', CountProductsView.as_view()),
    path('dashboard/count-sales/', CountSalesView.as_view()),
    path('dashboard/count-customers/', CountCustomersView.as_view()),
    path('dashboard/top-products/', TopSellingProductsView.as_view()),
    path('dashboard/low-stock-count/', LowStockProductsCountView.as_view()),
    path('dashboard/low-stock-alert/', LowStockProductsAlertView.as_view()),
    
    path('dashboard/total-revenue/', TotalRevenueView.as_view()),
    path('dashboard/monthly-sales-summary/', MonthlySalesSummaryView.as_view()),
    path('dashboard/sales-by-status/', SalesByStatusView.as_view()),
    path('dashboard/top-categories-sold/', TopCategoriesSoldView.as_view()),
    path('dashboard/out-of-stock-products/', ProductsOutOfStockView.as_view()),
    path('dashboard/total-stock-value/', TotalStockValueView.as_view()),
    path('dashboard/sales-today/', SalesTodayView.as_view()),
    path('dashboard/average-ticket-size/', AverageTicketSizeView.as_view()),
]
