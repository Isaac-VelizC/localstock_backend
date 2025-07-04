from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Ejecuta todos los seeders disponibles'

    def handle(self, *args, **kwargs):
        call_command('seed_roles')
        call_command('seed_rubros')
        call_command('seed_planes')
        # call_command('seed_units')
        self.stdout.write(self.style.SUCCESS('🎉 Todos los datos iniciales fueron cargados con éxito'))
