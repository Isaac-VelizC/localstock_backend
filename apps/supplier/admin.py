from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Supplier

# Register your models here.
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'photo_preview', 'nit', 'contact_name', 'email', 'phone', 'is_active', 'soft_deleted')
    list_filter = ('is_active', 'soft_deleted')
    search_fields = ('name', 'contact_name', 'nit', 'email')
    readonly_fields = ('created_at', 'updated_at')
    ordering =('-created_at',)

    def photo_preview(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="50"/>')
        return "-"
    photo_preview.short_description = "Foto"

    fieldsets = (
        (None, {
            'fields': ('name', 'contact_name', 'nit', 'email', 'phone')
        }),
        ('Estado', {
            'fields': ('is_active', 'soft_deleted')
        }),
        ('Tiempos', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )
