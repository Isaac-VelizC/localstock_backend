# seed_unidades.py
from django.core.management.base import BaseCommand
from apps.brand.models import Unit

class Command(BaseCommand):
    help = 'Seed unidades de medida para inventario y ventas'

    def handle(self, *args, **kwargs):
        unidades = [
            'Pieza', 'Kilogramo', 'Gramo', 'Litro', 'Mililitro',
            'Paquete', 'Caja', 'Docena', 'Metro', 'Centímetro',
            'Unidad', 'Rollo', 'Bolsa', 'botella', 'Barra',
            'Par', 'Set', 'Metro cuadrado', 'Metro cúbico'
        ]

        for name in unidades:
            obj, created = Unit.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Unidad creada: {name}'))
            else:
                self.stdout.write(f'Unidad ya existe: {name}')
