from django.core.validators import MinValueValidator, MaxValueValidator
from utils.base import SoftDeleteModel, ActiveManager
from apps.warehouse.models import Warehouse
from apps.customer.models import Customer
from apps.product.models import Product
from apps.stores.models import Store
from django.conf import settings
from django.db import models
import uuid

# Create your models here.
class Sale(SoftDeleteModel):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
        ('canceled', 'Cancelado'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Efectivo'),
        ('credit_card', 'Tarjeta de Crédito'),
        ('debit_card', 'Tarjeta de Débito'),
        ('transfer', 'Transferencia'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('partial', 'Parcial'),
        ('paid', 'Pagado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='sales')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='sales')
    sale_date = models.DateField(auto_now_add=True)
    sale_number = models.CharField(max_length=20, unique=True)
    invoice_number = models.CharField(max_length=100, null=True, blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    net_total = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=["invoice_number"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["store"]),
        ]

    def __str__(self):
        return f"Venta {self.invoice_number}"

class SaleDetail(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    