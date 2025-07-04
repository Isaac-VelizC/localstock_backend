from django.urls import path
from .views import StoreConfigView, ChangePlanTemporaryView, RubroListView, CountryListView

urlpatterns = [
    path('config/', StoreConfigView.as_view(), name='store-config'),
    path('rubros/list/', RubroListView.as_view(), name='store-rubros'),
    path('change-plan/', ChangePlanTemporaryView.as_view(), name='store-change-plan'),
    path('countries/', CountryListView.as_view(), name='country-list'),
]
