from .models import Product, ProductImages, ProductPriceHistory
from django.contrib.contenttypes.models import ContentType
from apps.warehouse.models import UserWarehouseAccess
from apps.brand.serializers import UnitSerializer
from django.db import transaction, IntegrityError
from rest_framework import serializers

class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ['id', 'image', 'is_primary', 'alt_text', 'order', 'created_at']

class ProductBaseSerializer(serializers.ModelSerializer):
    def validate_unique_fields(self, data):
        user = self.context['request'].user
        store = getattr(user, 'store', None)
        data_to_check = {
            'name': data.get('name'),
            'code': data.get('code'),
            'slug': data.get('slug'),
            'barcode': data.get('barcode'),
        }

        for field, value in data_to_check.items():
            if not value:
                continue
            # Excluir el propio objeto en update
            qs = Product.objects.filter(store=store, **{field: value})
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    field: f"Ya existe un producto con este {field} en esta tienda."
                })

    def validate_prices(self, data):
        purchase_price = data.get('purchase_price')
        sale_price = data.get('sale_price')

        if purchase_price is not None and sale_price is not None:
            if sale_price < purchase_price:
                raise serializers.ValidationError({
                    "sale_price": "El precio de venta no puede ser menor que el precio de compra."
                })

    def validate(self, data):
        self.validate_unique_fields(data)
        self.validate_prices(data)
        return data

class ProductCreateSerializer(ProductBaseSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'barcode', 'slug', 'purchase_price', 'sale_price',
            'unit', 'stock', 'brand', 'category', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        store = getattr(user, 'store', None)

        if not store:
            raise serializers.ValidationError("El usuario no tiene una tienda asignada.")
        access = UserWarehouseAccess.objects.filter(user=user, is_default=True).first()
        if not access:
            raise serializers.ValidationError("No tienes un almacén asignado por defecto.")

        warehouse = access.warehouse

        try:
            product = Product.objects.create(
                store=store,
                warehouse=warehouse,
                created_by=user,
                **validated_data
            )
            return product

        except IntegrityError as e:
            error_msg = str(e).lower()
            field = 'non_field_errors'
            if 'store_id, name' in error_msg:
                field = 'name'
            elif 'store_id, code' in error_msg:
                field = 'code'
            elif 'store_id, slug' in error_msg:
                field = 'slug'
            elif 'store_id, barcode' in error_msg:
                field = 'barcode'

            raise serializers.ValidationError({
                field: f"Ya existe un producto con este {field} en esta tienda."
            })

class ProductUpdateSerializer(ProductBaseSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 'code', 'barcode', 'slug', 'purchase_price', 'sale_price',
            'unit', 'stock', 'brand', 'category', 'is_active'
        ]

    @transaction.atomic
    def update(self, instance, validated_data):
        # Actualiza solo los campos permitidos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ProductHistoryPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPriceHistory
        fields = ['id', 'purchase_price', 'sale_price', 'changed_at', 'changed_by']

class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    brand = serializers.CharField(source='brand.name', read_only=True)
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'code', 'barcode', 'purchase_price', 'sale_price',
            'stock', 'brand', 'category', 'created_at', 'updated_at', 'is_active'
        ]

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    unit = UnitSerializer(read_only=True)
    brand = serializers.CharField(source='brand.name', read_only=True)
    images = ProductImagesSerializer(many=True, read_only=True)
    history_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id']
        extra_kwargs = {'is_active': {'default': True}}

    def get_history_price(self, obj):
        history = ProductPriceHistory.objects.filter(
            content_type=ContentType.objects.get_for_model(Product),
            object_id=obj.id
        ).order_by('-changed_at')
        return ProductHistoryPriceSerializer(history, many=True).data

class ProductSearchSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'code', 'barcode', 'sale_price']
        
class ProductBarcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'barcode', 'sale_price', 'stock']
        read_only_fields = fields

class ProductPurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'code', 'barcode', 'purchase_price',
            'unit', 'brand', 'description',
        ]