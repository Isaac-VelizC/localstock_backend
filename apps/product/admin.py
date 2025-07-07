from django.contrib import admin
from .models import Product

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'barcode', 'category', 'brand', 'sale_price', 'stock', 'is_active', 'soft_deleted')
    list_filter = ('is_active', 'soft_deleted', 'category', 'brand')
    search_fields = ('name', 'code', 'barcode', 'slug')
    list_editable = ('sale_price', 'stock', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'barcode', 'category', 'brand', 'unit')
        }),
        ('Precios y Stock', {
            'fields': ('purchase_price', 'sale_price', 'stock')
        }),
        ('Estado', {
            'fields': ('is_active', 'soft_deleted')
        }),
        ('Tiempos', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )
