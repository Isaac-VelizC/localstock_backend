from django.contrib import admin
from .models import Category

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'is_active', 'created_at')
    search_fields = ('name', 'store__name')
    list_filter = ('is_active', 'store__name' )