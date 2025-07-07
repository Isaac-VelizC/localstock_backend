from django.core.validators import RegexValidator
from django_countries.fields import CountryField
from cloudinary.models import CloudinaryField
from utils.base import SoftDeleteModel, ActiveManager
from apps.stores.models import Store
from django.db import models
import uuid

# Create your models here.
class Supplier(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    photo = CloudinaryField('suppliers', blank=True, null=True)
    contact_name = models.CharField(max_length=100)
    phone = models.CharField(
        max_length=20, blank=True, null=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="El número de teléfono debe tener entre 9 y 15 dígitos"
        )]
    )
    email = models.EmailField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    nit = models.CharField(max_length=50, blank=True, null=True)
    country = CountryField(default='BO')
    city = models.CharField(max_length=50, null=True, blank=True)
    website = models.CharField(max_length=150, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='suppliers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveManager()      # Manager por defecto (no eliminados)
    all_objects = models.Manager() # Manager que incluye todo

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['name']
        unique_together = [
            ('store', 'name'),
        ]