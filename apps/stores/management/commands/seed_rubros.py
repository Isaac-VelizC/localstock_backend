from django.core.management.base import BaseCommand
from apps.stores.models import Rubro

class Command(BaseCommand):
    help = 'Crea rubros iniciales'

    def handle(self, *args, **kwargs):
        rubros = ['Minimarkets', 'Ferreterías', 'Papeleria', 'Venta de Ropa', 'Otro']
        for name in rubros:
            obj, created = Rubro.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✔ Rubro creado: {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠ Rubro ya existe: {name}'))
