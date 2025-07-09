from apps.customer.serializers import CustomerSerializer
from apps.product.serializers import ProductItemSerializer
from rest_framework import serializers
from .models import Sale, SaleDetail

class SaleListSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    payment_status_display = serializers.SerializerMethodField()
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'sale_number', 'sale_date', 'payment_status_display',
            'payment_status', 'customer', 'net_total', 'status', 'status_display', 'created_at', 'updated_at']

    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_payment_status_display(self, obj):
        return obj.get_payment_status_display()

class SaleDetailItemDetailSerializer(serializers.ModelSerializer):
    product = ProductItemSerializer(read_only=True)
    class Meta:
        model = SaleDetail
        fields = [ 'product', 'quantity', 'sale_price', 'discount', 'subtotal' ]

class SaleDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    payment_method_display = serializers.SerializerMethodField()
    payment_status_display = serializers.SerializerMethodField()
    customer = CustomerSerializer(read_only=True)
    user_name = serializers.CharField(source='user.username' ,read_only=True)
    details = SaleDetailItemDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'customer', 'sale_date', 'invoice_number',
            'total', 'tax_total', 'discount_total', 'net_total',
            'payment_status', 'payment_status_display', 'payment_method',
            'payment_method_display', 'status', 'status_display', 'notes',
            'created_by', 'user_name', 'details', 'sale_number'
        ]

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_payment_method_display(self, obj):
        return obj.get_payment_method_display()

    def get_payment_status_display(self, obj):
        return obj.get_payment_status_display()
