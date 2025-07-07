from django.core.validators import RegexValidator
from utils.base import SoftDeleteModel, ActiveManager
from apps.warehouse.models import Warehouse
from apps.stores.models import Store
from django.db import models
import uuid

# Create your models here.
class Customer(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    surnames = models.CharField(max_length=150)
    phone = models.CharField(
        max_length=20, blank=True, null=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="El número de teléfono debe tener entre 9 y 15 dígitos"
        )]
    )
    email = models.EmailField(max_length=100, blank=True, null=True)
    ci = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="customers")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveManager()      # Manager por defecto (no eliminados)
    all_objects = models.Manager() # Manager que incluye todo

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
        ]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.name