from rest_framework.exceptions import PermissionDenied
from .models import UserWarehouseAccess

def get_default_warehouse(user):
    access = UserWarehouseAccess.objects.filter(user=user, is_default=True).select_related('warehouse').first()
    if not access:
        raise PermissionDenied("No tienes un almacén asignado por defecto.")
    return access.warehouse
