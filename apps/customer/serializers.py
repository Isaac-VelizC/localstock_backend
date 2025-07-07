from rest_framework import serializers
from apps.warehouse.models import UserWarehouseAccess
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'surnames', 'phone', 'email', 'ci',
            'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'store', 'warehouse', 'created_at', 'updated_at']
    
    def validate(self, data):
        phone = data.get('phone') or getattr(self.instance, 'phone', None)
        email = data.get('email') or getattr(self.instance, 'email', None)
        if not phone and not email:
            raise serializers.ValidationError("Debe proporcionar al menos un teléfono o un correo electrónico de contacto.")

        ci = data.get('ci')
        store = self.context['request'].user.store

        if ci is not None:
            qs = Customer.objects.filter(ci=ci, store=store, soft_deleted=False)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            if qs.exists():
                raise serializers.ValidationError({"ci": "Este CI ya está registrado para esta tienda."})

        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        store = getattr(user, 'store', None)
        if not store:
            raise serializers.ValidationError("El usuario no tiene una tienda asignada.")
        
        # Buscar el almacén por defecto del usuario
        access = UserWarehouseAccess.objects.filter(user=user, is_default=True).first()
        if not access:
            raise serializers.ValidationError("No tienes un almacén asignado por defecto.")

        return Customer.objects.create(store=store, warehouse=access.warehouse, **validated_data)

class CustomerSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'surnames', 'ci']