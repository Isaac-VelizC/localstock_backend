from django.core.management.base import BaseCommand
from apps.stores.models import Plan

class Command(BaseCommand):
    help = 'Crea planes de suscripción'

    def handle(self, *args, **kwargs):
        planes = [
            {
                'name': 'Básico',
                'price': 0.00,
                'max_users': 1,
                'max_products': 100,
                'features': {
                    "backup": False,
                    "soporte": False
                }
            },
            {
                'name': 'Pro',
                'price': 19.99,
                'max_users': 5,
                'max_products': 1000,
                'features': {
                    "backup": True,
                    "soporte": True
                }
            },
            {
                'name': 'Empresarial',
                'price': 49.99,
                'max_users': 20,
                'max_products': 5000,
                'features': {
                    "backup": True,
                    "soporte": True,
                    "acceso_api": True
                }
            },
        ]

        for plan in planes:
            obj, created = Plan.objects.get_or_create(name=plan['name'], defaults={
                'price': plan['price'],
                'max_users': plan['max_users'],
                'max_products': plan['max_products'],
                'features': plan['features']
            })
            if created:
                self.stdout.write(self.style.SUCCESS(f'✔ Plan creado: {plan["name"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠ Plan ya existe: {plan["name"]}'))
