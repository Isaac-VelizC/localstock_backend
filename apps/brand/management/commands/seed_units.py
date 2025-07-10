# seed_unidades.py
from django.core.management.base import BaseCommand
from apps.brand.models import Unit

class Command(BaseCommand):
    help = 'Seed unidades de medida para inventario y ventas'

    def handle(self, *args, **kwargs):
        unidades = [
            {"name": "Pieza", "abbreviation": "pz", "unit_type": "unidad"},
            {"name": "Kilogramo", "abbreviation": "kg", "unit_type": "peso", "conversion_factor": 1.0},
            {"name": "Gramo", "abbreviation": "g", "unit_type": "peso", "conversion_factor": 0.001},
            {"name": "Litro", "abbreviation": "L", "unit_type": "volumen", "conversion_factor": 1.0},
            {"name": "Mililitro", "abbreviation": "ml", "unit_type": "volumen", "conversion_factor": 0.001},
            {"name": "Paquete", "abbreviation": "paq", "unit_type": "unidad"},
            {"name": "Caja", "abbreviation": "cj", "unit_type": "unidad"},
            {"name": "Docena", "abbreviation": "dz", "unit_type": "unidad", "conversion_factor": 12},
            {"name": "Metro", "abbreviation": "m", "unit_type": "longitud", "conversion_factor": 1.0},
            {"name": "Centímetro", "abbreviation": "cm", "unit_type": "longitud", "conversion_factor": 0.01},
            {"name": "Unidad", "abbreviation": "u", "unit_type": "unidad"},
            {"name": "Rollo", "abbreviation": "rl", "unit_type": "unidad"},
            {"name": "Bolsa", "abbreviation": "bl", "unit_type": "unidad"},
            {"name": "Botella", "abbreviation": "bt", "unit_type": "unidad"},
            {"name": "Barra", "abbreviation": "br", "unit_type": "unidad"},
            {"name": "Par", "abbreviation": "pr", "unit_type": "unidad", "conversion_factor": 2},
            {"name": "Set", "abbreviation": "st", "unit_type": "unidad"},
            {"name": "Metro cuadrado", "abbreviation": "m²", "unit_type": "superficie"},
            {"name": "Metro cúbico", "abbreviation": "m³", "unit_type": "volumen"},
        ]

        for unidad in unidades:
            obj, created = Unit.objects.get_or_create(
                name=unidad["name"],
                defaults={
                    "abbreviation": unidad.get("abbreviation", ""),
                    "unit_type": unidad.get("unit_type", ""),
                    "conversion_factor": unidad.get("conversion_factor", 1.0)
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Unidad creada: {obj}'))
            else:
                self.stdout.write(f'ℹ️ Unidad ya existe: {obj}')
