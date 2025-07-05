from rest_framework import serializers
from .models import Brand, Unit

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'description', 'website',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'store', 'logo', 'created_at', 'updated_at']

    def validate_name(self, value):
        store = self.context['request'].user.store
        # Query para marcas con ese nombre y tienda
        qs = Brand.objects.filter(store=store, name=value)
        # Si es edición, excluye el objeto actual para evitar falso positivo
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe una marca con ese nombre en esta tienda.")
        return value

class BrandSearchSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = [
            'id', 'name', 'abbreviation'
        ]
        read_only_fields =['id']

class UniSearchSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name']