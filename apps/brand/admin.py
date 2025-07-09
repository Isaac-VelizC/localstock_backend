from django.contrib import admin
from .models import Brand, Unit

# Register your models here.
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_at')
    search_fields = ('name', 'store__name')
    list_filter = ('is_active',)

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'unit_type')
    list_filter = ('name', 'abbreviation')