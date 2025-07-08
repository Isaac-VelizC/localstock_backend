from django.core.validators import MinValueValidator, MaxValueValidator
from utils.base import SoftDeleteModel, ActiveManager
from cloudinary.models import CloudinaryField
from apps.warehouse.models import Warehouse
from apps.supplier.models import Supplier
from apps.product.models import Product
from apps.stores.models import Store
from django.conf import settings
from django.db import models
import uuid

# Create your models here.
class Purchase(SoftDeleteModel):
    STATUS_CHOICES = [
        ('completed', 'Completado'),
        ('pending', 'Pendiente'),
        ('canceled', 'Cancelado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchases')
    photo_invoice = CloudinaryField('purchase', blank=True, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='purchases')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='purchases')
    invoice_number = models.CharField(max_length=100)
    purchase_date = models.DateField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    net_total = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        unique_together = [
            ('store', 'invoice_number'),
        ]

    def __str__(self):
        return f"Compra {self.invoice_number}"
    
class PurchaseDetail(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"