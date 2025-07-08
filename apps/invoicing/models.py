from apps.warehouse.models import Warehouse
from django.db import models

class InvoiceCounter(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    date = models.DateField()
    operation_type = models.CharField(max_length=20, default='sale')
    last_number = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('warehouse', 'date', 'operation_type')