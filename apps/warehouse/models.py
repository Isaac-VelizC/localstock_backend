from django.db import models
from apps.stores.models import Store
from apps.accounts.models import User, Role
import uuid

# Create your models here.
class Warehouse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="warehouses")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    soft_delete = models.BooleanField(default=False)
        
    class Meta:
        unique_together = ('store', 'code')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.store.name}"
    
class UserWarehouseAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'warehouse')  # para que no se repita acceso

