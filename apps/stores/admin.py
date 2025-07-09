from django.contrib import admin
from .models import Store, Plan, Rubro

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'plan', 'rubro', 'country', 'created_at')
    list_filter = ('rubro', 'plan')
    search_fields = ('name', 'code', 'country')
    readonly_fields = ('created_at', 'updated_at')
    ordering =('-created_at',)

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'max_users', 'max_products')
    search_fields = ('name', )
    ordering =('name',)

@admin.register(Rubro)
class RubroAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    ordering =('name',)
