from django.contrib import admin
from .models import Sale

# Register your models here.

@admin.register(Sale)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('customer', 'invoice_number', 'sale_date', 'net_total', 'status', 'created_by', 'created_at', 'soft_deleted')
    list_filter = ('status', 'store__name', 'payment_method')
    search_fields = ('customer', 'invoice_number', 'sale_date')
    readonly_fields = ('created_at', 'updated_at')
    ordering =('-created_at',)
