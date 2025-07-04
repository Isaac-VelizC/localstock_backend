from django.db import models
from decimal import Decimal
from django_countries.fields import CountryField
import uuid

# Create your models here.
class Rubro(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Plan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_users = models.IntegerField(null=True, blank=True)
    max_products = models.IntegerField(null=True, blank=True)
    features = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name
    
class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, blank=True, null=True) 
    logo = models.TextField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    rubro = models.ForeignKey(Rubro, on_delete=models.SET_NULL, null=True)
    country = CountryField(default='BO')  # ISO-3166
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class GeneralSetting(models.Model):
    store = models.OneToOneField(Store, on_delete=models.CASCADE, related_name='settings')
    timezone = models.CharField(max_length=50, default='America/La_Paz')
    idioma = models.CharField(max_length=10, default='es')
    currency = models.CharField(max_length=10, default='BOB')
    tax_enabled = models.BooleanField(default=False)
    theme = models.CharField(max_length=20, default='light')
    alerts_stock = models.BooleanField(default=True)
    stock_minimo = models.IntegerField(default=5)
    notification_email = models.BooleanField(default=False)
    auto_update_price_on_purchase = models.BooleanField(default=False)
    margin_percentage = models.DecimalField(default=Decimal('20.0'), max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
