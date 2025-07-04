from rest_framework import serializers
from .models import Warehouse

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = [
            'id', 'name', 'code', 'store', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['store', 'created_at', 'updated_at']

    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        store = getattr(user, 'store', None)

        if not store:
            raise serializers.ValidationError("El usuario no tiene una tienda asignada.")

        # Para creación
        code = attrs.get('code')

        queryset = Warehouse.objects.filter(
            store=store,
            code=code,
            soft_delete=False,  # evitar duplicados con los que no están eliminados
        )

        # Para edición, excluye el objeto actual
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)

        if queryset.exists():
            raise serializers.ValidationError(
                {"code": "Ya existe un almacén activo o no eliminado con este código en la tienda."}
            )

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        store = getattr(user, 'store', None)

        if not store:
            raise serializers.ValidationError("El usuario no tiene una tienda asignada.")

        return Warehouse.objects.create(store=store, **validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
