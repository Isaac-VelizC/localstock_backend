from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from cloudinary.models import CloudinaryField
from apps.warehouse.models import Warehouse
from apps.brand.models import Unit, Brand
from apps.category.models import Category
from django.utils.text import slugify
from apps.stores.models import Store
from autoslug import AutoSlugField
from django.db import models
from django.conf import settings
import uuid

# Create your models here.
# Managers para soft delete
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(soft_deleted=False)

# Modelo Producto principal
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='generate_slug', unique_with=['store'], slugify=slugify, always_update=True)
    code = models.CharField(max_length=100, db_index=True, null=True, blank=True )
    barcode = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, default=11)
    stock = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    reserved_stock = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    soft_deleted = models.BooleanField(default=False)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        unique_together = [
            ('store', 'name'),
            ('store', 'code'),
            ('store', 'slug'),
            ('store', 'barcode'),
        ]
        indexes = [
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['name', 'code'], name='product_name_code_idx'),
        ]
    
    @property
    def available_stock(self):
        return self.stock - self.reserved_stock
    
    def generate_slug(self):
        return f"{self.code}-{self.name}"
    
    def __str__(self):
        return self.name or f"Producto sin nombre ({self.pk})"
    
    def delete(self, *args, **kwargs):
        self.soft_deleted = True
        self.save()

    def save(self, *args, **kwargs):
        if not self.barcode:
            self.barcode = self.generate_barcode()
        super().save(*args, **kwargs)

    def generate_barcode(self):
        return str(uuid.uuid4()).replace('-', '')[:12]

# Modelo para gestionar imágenes del producto
class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField()
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'order')
        ordering = ['order', 'created_at']
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            # Desactivar otras imágenes primarias del mismo producto
            ProductImages.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Imagen de {self.product.name} (Primaria: {self.is_primary})"

# Historial de precios usando GenericForeignKey para flexibilidad
class ProductPriceHistory(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')

    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        name = getattr(self.content_object, 'name', 'Producto')
        return f"{name} - {self.changed_at.date()} - Compra: {self.purchase_price}, Venta: {self.sale_price}"
