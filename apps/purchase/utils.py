from apps.product.models import ProductPriceHistory, Product
from apps.inventory.models import InventoryTransaction
from django.db import transaction
from decimal import Decimal

def calculate_sale_price(purchase_price, margin_percentage):
    if margin_percentage is None:
        margin_percentage = 0
    return round(Decimal(purchase_price) * (1 + (Decimal(margin_percentage) / 100)), 2)

def handle_purchase_price_update(product, new_price, user, config=None):
    """
    Se encarga de actualizar el precio del producto (si aplica)
    y registrar el historial de precios de compra.
    """
    auto_update = getattr(config, 'auto_update_price_on_purchase', False)
    margin = getattr(config, 'margin_percentage', 0)

    if auto_update:
        product.purchase_price = new_price
        product.sale_price = calculate_sale_price(new_price, margin)
        product.save(update_fields=['purchase_price', 'sale_price'])

    # Registrar historial de precios SIEMPRE
    ProductPriceHistory.objects.create(
        content_object=product,
        purchase_price=new_price,
        sale_price=product.sale_price,
        changed_by=user
    )

def procesar_confirmacion(purchase, user):
    """
    Confirma una compra pendiente y actualiza stock.
    """
    with transaction.atomic():
        inventory_logs = []
        updated_products = []
        warehouse = purchase.warehouse

        config = getattr(purchase.store, 'settings', None)

        for detail in purchase.details.select_related('product'):
            product = detail.product
            quantity = detail.quantity

            product.stock += quantity
            # Si manejas stock reservado:
            updated_products.append(product)

            inventory_logs.append(InventoryTransaction(
                product=product,
                quantity=quantity,
                type='entrada',
                reason='Confirmación de compra',
                reference_type='Purchase',
                reference_id=purchase.id,
                user=user,
                warehouse=warehouse,
                store=purchase.store
            ))

            handle_purchase_price_update(
                product=product,
                new_price=detail.purchase_price,
                user=user,
                config=config
            )

        InventoryTransaction.objects.bulk_create(inventory_logs)
        Product.objects.bulk_update(updated_products, ['stock'])

        purchase.status = 'completed'
        purchase.save()

def procesar_cancelacion(purchase, user):
    """
    Cancela una compra. Si estaba completada, revierte el stock.
    """
    with transaction.atomic():
        updated_products = []
        inventory_logs = []
        warehouse = purchase.warehouse
        store = purchase.store

        if purchase.status == 'completed':
            for detail in purchase.details.select_related('product'):
                product = detail.product
                quantity = detail.quantity

                # Revertir stock
                product.stock = max(0, product.stock - quantity)
                updated_products.append(product)

                inventory_logs.append(InventoryTransaction(
                    product=product,
                    quantity=quantity,
                    type='ajuste',
                    reason='Cancelación de compra',
                    reference_type='Purchase',
                    reference_id=purchase.id,
                    user=user,
                    warehouse=warehouse,
                    store=store
                ))

            InventoryTransaction.objects.bulk_create(inventory_logs)
            Product.objects.bulk_update(updated_products, ['stock'])

        purchase.status = 'canceled'
        purchase.save()
