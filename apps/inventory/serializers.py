from .models import InventoryTransaction
from rest_framework import serializers

class InventoryTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryTransaction
        fields = ['id', 'product', 'warehouse', 'quantity',
                  'type', 'reason', 'user_name', 'created_at', 'reference_id']
        read_only_fields = ['id', 'created_at', 'type', 'warehouse', 'reference_id',]
        
    def validate_quantity(self, value):
        if value == 0:
            raise serializers.ValidationError("La cantidad no puede ser cero.")
        return value
    
    def validate(self, data):
        type = data.get('type')
        quantity = data.get('quantity')

        if type == 'entrada' and quantity < 0:
            data['quantity'] = abs(quantity)
        elif type == 'salida' and quantity > 0:
            data['quantity'] = -abs(quantity)

        return data