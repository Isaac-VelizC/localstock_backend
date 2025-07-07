from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from apps.warehouse.models import Warehouse
from apps.product.models import Product
from apps.stores.models import Store
from django.conf import settings
from django.db import models
import uuid

# Create your models here.
class InventoryTransaction(models.Model):
    class TransactionType(models.TextChoices):
        ENTRADA = 'entrada', _('Entrada')
        SALIDA = 'salida', _('Salida')
        AJUSTE = 'ajuste', _('Ajuste')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="transactions")
    quantity = models.IntegerField()
    type = models.CharField(max_length=20, choices=TransactionType.choices, default=TransactionType.AJUSTE)
    reason = models.TextField(max_length=150, blank=True, null=True)
    reference_type = models.CharField(max_length=50, blank=True, null=True)
    reference_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")

    def clean(self):
        if self.store is None:
            raise ValidationError({'store': 'El campo tienda (store) es obligatorio.'})
        
        if self.warehouse is None:
            raise ValidationError({'store': 'El campo almacén (warehouse) es obligatorio.'})
        
        # Validar cantidad no nula
        if self.quantity == 0:
            raise ValidationError("La cantidad no puede ser cero.")

        # Entradas deben ser positivas, salidas negativas
        if self.type == self.TransactionType.SALIDA and self.quantity > 0:
            self.quantity = -self.quantity
        
        if self.type == self.TransactionType.ENTRADA and self.quantity < 0:
            self.quantity = -self.quantity

    def save(self, *args, **kwargs):
        self.full_clean()  # Ejecutar clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.get_type_display()} de {abs(self.quantity)} × {self.product.name} ({self.created_at.strftime('%Y-%m-%d')})"

    class Meta:
        verbose_name = "Transacción de Inventario"
        verbose_name_plural = "Transacciones de Inventario"
        ordering = ['-created_at']
