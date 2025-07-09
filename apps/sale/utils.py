from apps.inventory.models import InventoryTransaction
from apps.product.models import Product
from rest_framework import serializers
from django.db import transaction
from .models import Sale

def generate_sale_number_by_store(store):
    prefix = f"{store.code}-SL"
    last_sale = Sale.objects.filter(
        store=store,
        sale_number__startswith=prefix
    ).order_by('-sale_number').first()
    
    if last_sale and last_sale.sale_number:
        try:
            last_number = int(last_sale.sale_number.split('-')[-1])
        except ValueError:
            last_number = 0
    else:
        last_number = 0

    new_number = last_number + 1
    return f"{prefix}-{str(new_number).zfill(5)}"

def procesar_confirmacion(sale, user):
    """
    Confirma una venta pendiente: descuenta stock y libera reservas.
    """
    if sale.status == 'completed':
        raise serializers.ValidationError("La venta ya ha sido confirmada.")
    if sale.status == 'canceled':
        raise serializers.ValidationError("No se puede confirmar una venta cancelada.")

    with transaction.atomic():
        inventory_logs = []
        updated_products = []
        warehouse = sale.warehouse
        config = getattr(sale.store, 'settings', None)

        for detail in sale.details.select_related('product'):
            product = detail.product
            quantity = detail.quantity

            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Stock insuficiente para {product.name}. Quedan {product.stock} unidades."
                )

            # Liberar reservas si estaba pendiente
            if sale.status == 'pending':
                product.reserved_stock = max(0, product.reserved_stock - quantity)

            # Descontar stock
            product.stock -= quantity
            updated_products.append(product)

            inventory_logs.append(InventoryTransaction(
                product=product,
                quantity=quantity,
                type='salida',
                reason='Confirmación de venta',
                reference_type='Sale',
                reference_id=sale.id,
                user=user,
                warehouse=warehouse,
                store=sale.store
            ))

        InventoryTransaction.objects.bulk_create(inventory_logs)
        Product.objects.bulk_update(updated_products, ['stock', 'reserved_stock'])

        sale.status = 'completed'
        sale.save()

def procesar_cancelacion(sale, user):
    """
    Cancela una venta. Si estaba completada, revierte el stock.
    """
    if sale.status == 'canceled':
        raise serializers.ValidationError("La venta ya fue cancelada.")

    with transaction.atomic():
        updated_products = []
        inventory_logs = []
        warehouse = sale.warehouse
        store = sale.store

        for detail in sale.details.select_related('product'):
            product = detail.product
            quantity = detail.quantity

            # Revertir según estado anterior
            if sale.status == 'pending':
                product.reserved_stock = max(0, product.reserved_stock - quantity)
            elif sale.status == 'completed':
                product.stock = product.stock + quantity  # Reponer stock

            updated_products.append(product)

            inventory_logs.append(InventoryTransaction(
                product=product,
                quantity=quantity,
                type='ajuste',
                reason='Cancelación de venta',
                reference_type='Sale',
                reference_id=sale.id,
                user=user,
                warehouse=warehouse,
                store=store
            ))

        InventoryTransaction.objects.bulk_create(inventory_logs)
        Product.objects.bulk_update(updated_products, ['stock', 'reserved_stock'])

        sale.status = 'canceled'
        sale.save()
