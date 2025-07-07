from django.contrib import admin
from .models import Customer

# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'surnames', 'ci', 'email', 'phone', 'is_active', 'soft_deleted')
    list_filter = ('is_active', 'soft_deleted')
    search_fields = ('name', 'surnames', 'ci')
    list_editable = ('phone',)
    readonly_fields = ('created_at', 'updated_at')
    ordering =('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('name', 'surnames', 'ci', 'email', 'phone')
        }),
        ('Estado', {
            'fields': ('is_active', 'soft_deleted')
        }),
        ('Tiempos', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )
