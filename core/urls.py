from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # refrescar el access token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # verificar si un token sigue siendo válido
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/stores/', include('apps.stores.urls')),
    path('api/w/', include('apps.warehouse.urls')),
    path('api/b/', include('apps.brand.urls')),
    path('api/c/', include('apps.category.urls')),
    path('api/p/', include('apps.product.urls')),
    path('api/s/', include('apps.supplier.urls')),
    path('api/cli/', include('apps.customer.urls')),
    path('api/i/', include('apps.inventory.urls')),
    path('api/purchase/', include('apps.purchase.urls')),
    path('api/sale/', include('apps.sale.urls')),
    path('api/a/', include('apps.analytics.urls')),
]
