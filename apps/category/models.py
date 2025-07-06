from django.db import models
from autoslug import AutoSlugField
from apps.stores.models import Store
from django.utils.text import slugify

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='categories')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subcategories', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    slug = AutoSlugField(populate_from='generate_slug', unique_with=['store', 'parent'], slugify=slugify, always_update=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_slug(self):
        if self.parent:
            return f"{self.parent.slug}-{self.name}"
        return self.name

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' / '.join(full_path[::-1]) + f" ({self.store.name})"

    class Meta:
        # Slug único por store y parent (redundante pero segura)
        unique_together = ['store', 'parent', 'slug']
        indexes = [
            models.Index(fields=['slug', 'parent']),  # Mejorar búsquedas
        ]
