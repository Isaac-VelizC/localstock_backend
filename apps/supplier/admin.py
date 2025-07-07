from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Supplier

# Register your models here.
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'photo_preview')

    def photo_preview(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="50"/>')
        return "-"
    photo_preview.short_description = "Foto"
