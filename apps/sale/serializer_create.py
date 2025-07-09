from apps.invoicing.utils import generate_invoice_number
from apps.warehouse.utils import get_default_warehouse
from apps.inventory.models import InventoryTransaction
from .utils import generate_sale_number_by_store
from apps.product.models import Product
from rest_framework import serializers
from .models import Sale, SaleDetail
from django.db import transaction
from decimal import Decimal

class SaleDetailItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleDetail
        fields = ['product', 'quantity', 'discount', 'sale_price', 'subtotal']
        read_only_fields = ['subtotal', 'sale', 'tax_rate', 'sale_price']

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity')
        # Validar que product y quantity estén presentes
        if product is None:
            raise serializers.ValidationError({'product': 'Producto es requerido.'})
        if quantity is None:
            raise serializers.ValidationError({'quantity': 'Cantidad es requerida.'})
        # Validar que el producto tenga stock suficiente
        if not hasattr(product, 'stock'):
            raise serializers.ValidationError({'product': 'Producto inválido.'})

        if product.stock < quantity:
            raise serializers.ValidationError({'quantity': f'Stock insuficiente. Disponible: {product.stock}.'})

        return data
    
class SaleCreateSerializer(serializers.ModelSerializer):
    details = SaleDetailItemSerializer(many=True)
    class Meta:
        model = Sale
        fields = [
            'customer', 'payment_status','payment_method', 'status', 
            'notes', 'details'
        ]
        read_only_fields = [
            'total', 'tax_total', 'net_total', 'invoice_number', 'sale_number', 'user',
            'created_at', 'updated_at', 'store', 'warehouse', 'discount_total'
        ]

    def validar_stock(self, product, quantity, status):
        if status == 'completed' and product.stock < quantity:
            raise serializers.ValidationError(f"Stock insuficiente para {product.name}.")
        if status == 'pending' and product.stock - product.reserved_stock < quantity:
            raise serializers.ValidationError(f"Stock insuficiente para reservar {product.name}.")
        
    def create(self, validated_data):
        details_data = validated_data.pop('details')
        request = self.context['request']
        user = request.user
        store = getattr(user, 'store', None)

        if not store:
            raise serializers.ValidationError("El usuario no tiene una tienda asignada.")

        warehouse = get_default_warehouse(user)
        status = validated_data.get('status', 'completed')
        invoice_number = generate_invoice_number(warehouse)
        validated_data['sale_number'] = generate_sale_number_by_store(store)

        product_ids = [detail['product'].id for detail in details_data]
        # Validar duplicados
        if len(set(product_ids)) != len(product_ids):
            raise serializers.ValidationError("No se permiten productos duplicados en la compra.")

        products = {product.id: product for product in Product.objects.filter(id__in=product_ids).select_for_update()}

        # Validación previa de stock o reservas
        for detail in details_data:
            product = products[detail['product'].id]
            quantity = detail['quantity']
            self.validar_stock(product, quantity, status)
        
        with transaction.atomic():
            # Crear venta
            sale = Sale.objects.create(
                created_by=user,
                warehouse=warehouse,
                store=store,
                invoice_number=invoice_number,
                **validated_data
            )
            sale_details = []
            inventory_logs = []
            total, discount_total = 0, 0
            
            for detail_data in details_data:
                product = products[detail_data['product'].id]
                quantity = detail_data['quantity']
                discount = Decimal(str(detail_data['discount']))
                price = product.sale_price

                # Descontar stock SOLO si la venta está completada
                if status == 'completed':
                    product.stock -= quantity
                    inventory_logs.append(InventoryTransaction(
                    product=product,
                    warehouse=warehouse,
                    quantity=quantity,
                    type='salida',
                    reason='Venta registrada',
                    reference_type='Sale',
                    reference_id=sale.id,
                    user=user,
                    store=store
                ))  # ✅ Solo lo crea en memoria

                elif status == 'pending':
                    product.reserved_stock += quantity
                
                subtotal = (price * quantity) * (1 - (discount / 100))
                total += price * quantity
                discount_total += (price * quantity) - subtotal
                sale_details.append(SaleDetail(sale=sale, sale_price = price, subtotal = subtotal, **detail_data))

            # Bulk create detalles y movimientos
            SaleDetail.objects.bulk_create(sale_details)
            InventoryTransaction.objects.bulk_create(inventory_logs)
            # Bulk update productos modificados
            Product.objects.bulk_update(products.values(), ['stock', 'reserved_stock'])
            # Calcular totales y guardar
            sale.total = total
            sale.discount_total = discount_total
            # TODO: Calcular tax_total si se requiere a futuro por producto
            sale.tax_total = 0 # sum((d['sale_price'] * d['quantity'] - (d['discount'] / 100 * d['sale_price'] * d['quantity'])) * d['tax_rate'] / 100 for d in details_data)
            sale.net_total = total - discount_total
            sale.save()

            return sale
    
    def update(self, instance, validated_data):
        request = self.context['request']
        user = request.user
        store = getattr(user, 'store', None)

        status = validated_data.get('status', instance.status)

        # Solo permitimos editar ventas en estado 'draft' o 'pending'
        if instance.status not in ['draft', 'pending']:
            raise serializers.ValidationError("Solo se pueden editar ventas en estado 'Pendiente' o 'Borrador'.")

        details_data = validated_data.pop('details', [])
        product_ids = [detail['product'].id for detail in details_data]

        if len(set(product_ids)) != len(product_ids):
            raise serializers.ValidationError("No se permiten productos duplicados en la venta.")

        products = {p.id: p for p in Product.objects.filter(id__in=product_ids).select_for_update()}

        with transaction.atomic():
            # Revertir stock/reservas de los detalles anteriores
            for old_detail in instance.details.select_related('product'):
                product = old_detail.product
                if instance.status == 'completed':
                    product.stock += old_detail.quantity
                elif instance.status == 'pending':
                    product.reserved_stock -= old_detail.quantity
                product.save()

            # Borrar detalles antiguos
            instance.details.all().delete()

            # Validar stock para los nuevos productos
            for detail in details_data:
                product = products[detail['product'].id]
                quantity = detail['quantity']
                self.validar_stock(product, quantity, status)

            sale_details = []
            inventory_logs = []
            total = discount_total = Decimal('0.00')

            for detail_data in details_data:
                product = products[detail_data['product'].id]
                quantity = Decimal(detail_data['quantity'])
                discount = Decimal(detail_data.get('discount', 0))
                price = product.sale_price

                # Stock actualizado según nuevo estado
                if status == 'completed':
                    product.stock -= quantity
                    inventory_logs.append(InventoryTransaction(
                        product=product,
                        warehouse=product.warehouse,
                        quantity=quantity,
                        type='salida',
                        reason='Venta actualizada',
                        reference_type='Sale',
                        reference_id=instance.id,
                        user=user,
                        store=store
                    ))
                elif status == 'pending':
                    product.reserved_stock += quantity

                subtotal = (price * quantity) * (1 - (discount / 100))
                total += price * quantity
                discount_total += (price * quantity) - subtotal

                sale_details.append(SaleDetail(
                    sale=instance,
                    product=product,
                    quantity=quantity,
                    discount=discount,
                    sale_price=price,
                    subtotal=subtotal
                ))

            SaleDetail.objects.bulk_create(sale_details)
            InventoryTransaction.objects.bulk_create(inventory_logs)
            Product.objects.bulk_update(products.values(), ['stock', 'reserved_stock'])

            instance.status = status
            instance.total = total
            instance.discount_total = discount_total
            instance.tax_total = Decimal('0.00')
            instance.net_total = total - discount_total

            # Actualizar otros campos editables de la venta
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            instance.save()

            return instance
