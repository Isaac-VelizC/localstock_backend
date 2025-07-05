from django.db import models
from apps.stores.models import Store
from cloudinary.models import CloudinaryField

# Create your models here.
class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=10)
    unit_type = models.CharField(max_length=50, blank=True, null=True)  # ej: peso, volumen
    conversion_factor = models.FloatField(default=1.0)  # para convertir a unidad base

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='brands')
    description = models.TextField(blank=True, null=True)
    logo = CloudinaryField('brands', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('store', 'name')
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.store.name}"