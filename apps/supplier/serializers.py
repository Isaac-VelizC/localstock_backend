from rest_framework import serializers
from .models import Supplier

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id', 'photo', 'contact_name', 'phone', 'email', 'address', 'nit',
            'country', 'city', 'website', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'store', 'created_at', 'updated_at']
    
    def validate(self, data):
        phone = data.get('phone') or getattr(self.instance, 'phone', None)
        email = data.get('email') or getattr(self.instance, 'email', None)
        if not phone and not email:
            raise serializers.ValidationError("Debe proporcionar al menos un teléfono o un correo electrónico de contacto.")

        nit = data.get('nit')
        store = self.context['request'].user.store

        if nit is not None:
            qs = Supplier.objects.filter(nit=nit, store=store, is_deleted=False)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            if qs.exists():
                raise serializers.ValidationError({"nit": "Este NIT ya está registrado para esta tienda."})

        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        store = getattr(user, 'store', None)
        if not store:
            raise serializers.ValidationError("El usuario no tiene una tienda asociada.")
        return Supplier.objects.create(store=store, **validated_data)

class SupplierSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'nit']