from apps.invoicing.utils import generate_invoice_number
from django.utils.translation import gettext_lazy as _
from apps.warehouse.utils import get_default_warehouse
from .models import Purchase, PurchaseDetail
from apps.product.models import Product
from rest_framework import serializers
from django.db import transaction
from decimal import Decimal

class PurchaseDetailCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDetail
        fields = [
            'product', 'quantity', 'purchase_price',
            'tax_rate', 'discount', 'subtotal'
        ]
        read_only_fields = ['subtotal', 'purchase']

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity')

        errors = {}
        if product is None:
            errors['product'] = _('Producto es requerido.')
        if quantity is None:
            errors['quantity'] = _('Cantidad es requerida.')
        elif quantity <= 0:
            errors['quantity'] = _('Cantidad debe ser mayor que cero.')

        if errors:
            raise serializers.ValidationError(errors)

        return data

class PurchaseCreateSerializer(serializers.ModelSerializer):
    details = PurchaseDetailCreateSerializer(many=True)
    class Meta:
        model = Purchase
        fields = [
            'id', 'supplier', 'status', 'details']
        read_only_fields = [
            'total', 'net_total', 'tax_total', 'user', 'invoice_number',
            'created_at', 'updated_at','discount_total'
        ]
    
    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        store = getattr(user, 'store', None)

        if not store:
            raise serializers.ValidationError("El usuario no tiene una tienda asignada.")

        warehouse = get_default_warehouse(user)
        invoice_number = generate_invoice_number(warehouse, 'purchase')

        # Extraemos y removemos detalles antes de crear la compra
        details_data = validated_data.pop('details')
        product_ids = [detail['product'].id for detail in details_data]
        # Validar duplicados
        if len(set(product_ids)) != len(product_ids):
            raise serializers.ValidationError("No se permiten productos duplicados en la compra.")

        # Precargamos productos con lock optimista
        products = {product.id: product for product in Product.objects.select_for_update().filter(id__in=product_ids)}
            
        with transaction.atomic():
            purchase = Purchase.objects.create(
                created_by=user,
                store=store,
                warehouse=warehouse,
                invoice_number=invoice_number,
                total=0,
                tax_total=0,
                discount_total=0,
                net_total=0,
                **validated_data
            )

            details_to_create = []

            total = tax_total = discount_total = 0

            for detail in details_data:
                product = products[detail['product'].id]

                if not product:
                    raise serializers.ValidationError(f"Producto no encontrado: {product}")

                quantity = Decimal(detail['quantity'])
                purchase_price = Decimal(detail['purchase_price'])
                discount_amt = Decimal(detail.get('discount', 0))
                tax_rate = Decimal(detail.get('tax_rate', 0))

                subtotal = (quantity * purchase_price) - discount_amt
                tax_amount = subtotal * (tax_rate / 100)

                total += quantity * purchase_price
                tax_total += tax_amount
                discount_total += discount_amt

                # Actualizar stock localmente
                product.stock += quantity
                # Registrar movimiento de inventario
                details_to_create.append(PurchaseDetail(
                    purchase=purchase,
                    product=product,
                    quantity=quantity,
                    purchase_price=purchase_price,
                    tax_rate=tax_rate,
                    discount=discount_amt,
                    subtotal=subtotal
                ))
            # Guardar en bloque
            PurchaseDetail.objects.bulk_create(details_to_create)

            net_total = total + tax_total - discount_total

            # Actualizar la compra
            purchase.total = total
            purchase.tax_total = tax_total
            purchase.discount_total = discount_total
            purchase.net_total = net_total
            purchase.save()

        return purchase
    
    def update(self, instance, validated_data):

        if instance.status != 'pending':
            raise serializers.ValidationError("Solo se pueden editar compras pendientes.")

        details_data = validated_data.pop('details')
        product_ids = [detail['product'].id for detail in details_data]

        if len(set(product_ids)) != len(product_ids):
            raise serializers.ValidationError("No se permiten productos duplicados.")

        products = {product.id: product for product in Product.objects.filter(id__in=product_ids).select_for_update()}

        with transaction.atomic():
            # Actualizar campos simples
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Eliminar detalles antiguos
            instance.details.all().delete()

            # Recalcular totales y registrar nuevos detalles
            total = tax_total = discount_total = 0
            new_details = []

            for detail in details_data:
                product = products[detail['product'].id]

                quantity = Decimal(detail['quantity'])
                purchase_price = Decimal(detail['purchase_price'])
                discount_amt = Decimal(detail.get('discount', 0))
                tax_rate = Decimal(detail.get('tax_rate', 0))

                subtotal = (quantity * purchase_price) - discount_amt
                tax_amount = subtotal * (tax_rate / 100)

                total += quantity * purchase_price
                tax_total += tax_amount
                discount_total += discount_amt

                new_details.append(PurchaseDetail(
                    purchase=instance,
                    product=product,
                    quantity=quantity,
                    purchase_price=purchase_price,
                    tax_rate=tax_rate,
                    discount=discount_amt,
                    subtotal=subtotal
                ))

            PurchaseDetail.objects.bulk_create(new_details)

            net_total = total + tax_total - discount_total

            # Actualizar totales
            instance.total = total
            instance.tax_total = tax_total
            instance.discount_total = discount_total
            instance.net_total = net_total
            instance.save()

        return instance
