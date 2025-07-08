from .models import InvoiceCounter
from django.utils.timezone import now
from django.db import transaction
from django.db.models import F

def generate_invoice_number(warehouse, operation_type='sale'):
    today = now().date()
    date_str = today.strftime('%Y%m%d')

    with transaction.atomic():
        counter, _ = InvoiceCounter.objects.select_for_update().get_or_create(
            warehouse=warehouse,
            date=today,
            operation_type=operation_type,  # Nuevo campo si deseas
            defaults={'last_number': 0}
        )
        counter.last_number = F('last_number') + 1
        counter.save()
        counter.refresh_from_db()

    if operation_type == 'purchase':
        invoice_number = f"P-{date_str}-{warehouse.code}-{counter.last_number:04d}"
    else:
        invoice_number = f"S-{date_str}-{warehouse.code}-{counter.last_number:04d}"

    return invoice_number
