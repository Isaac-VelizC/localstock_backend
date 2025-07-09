from django.contrib import admin
from .models import Purchase

# Register your models here.
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'invoice_number', 'purchase_date', 'net_total', 'status', 'created_by', 'created_at', 'soft_deleted')
    list_filter = ('status', 'store__name')
    search_fields = ('supplier', 'invoice_number', 'purchase_date')
    readonly_fields = ('created_at', 'updated_at')
    ordering =('-created_at',)
