from .models import Purchase, PurchaseDetail
from apps.product.serializers import ProductPurchaseItemSerializer
from apps.supplier.serializers import SupplierSerializer
from rest_framework import serializers

class PurchaseListSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    class Meta:
        model = Purchase
        fields = [
            'id', 'supplier', 'supplier_name', 'invoice_number', 'purchase_date',
            'status', 'status_display', 'net_total', 'created_at', 'updated_at'
        ]
    
    def get_status_display(self, obj):
        return obj.get_status_display()

class PurchaseDetailItemSerializer(serializers.ModelSerializer):
    product = ProductPurchaseItemSerializer(read_only=True)
    class Meta:
        model = PurchaseDetail
        fields = [
            'product', 'quantity', 'purchase_price', 'tax_rate', 'discount', 'subtotal'
        ]

class PurchaseDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    supplier = SupplierSerializer(read_only=True)
    details = PurchaseDetailItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.name' ,read_only=True)

    class Meta:
        model = Purchase
        fields = [
            'id', 'supplier', 'invoice_number', 'purchase_date',
            'total', 'tax_total', 'discount_total', 'status', 'status_display',
            'net_total', 'details', 'created_at', 'user_name', 'updated_at'
        ]
    
    def get_status_display(self, obj):
        return obj.get_status_display()