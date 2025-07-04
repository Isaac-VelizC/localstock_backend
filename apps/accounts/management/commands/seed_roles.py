from django.core.management.base import BaseCommand
from apps.accounts.models import Permission, Role
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Crea roles y permisos iniciales de forma modular'

    def handle(self, *args, **kwargs):
        # 1. Define los permisos por módulo y acción
        permisos_definidos = {
            "ventas": ["crear", "ver", "editar", "eliminar"],
            "productos": ["crear", "ver", "editar", "eliminar"],
            "clientes": ["crear", "ver", "editar", "eliminar"],
            "usuarios": ["crear", "ver", "editar", "eliminar"],
            "gastos": ["crear", "ver"],
            "inventario": ["ver", "editar"],
            "reportes": ["ver", "exportar", "imprimir"],
            "configuracion": ["ver", "editar"],
            "historial": ["ver"],
        }

        permisos_obj = {}

        # 2. Crea todos los permisos de forma sistemática
        for modulo, acciones in permisos_definidos.items():
            for accion in acciones:
                nombre = f"{modulo}.{accion}"
                slug = slugify(nombre)
                permiso, creado = Permission.objects.get_or_create(
                    name=nombre,
                    defaults={
                        "module": modulo,
                        "action": accion,
                        "slug": slug
                    }
                )
                permisos_obj[nombre] = permiso
                self.stdout.write(
                    self.style.SUCCESS(f"{'✔' if creado else '⚠'} Permiso {'creado' if creado else 'ya existe'}: {nombre}")
                )

        # 3. Define roles y permisos asociados
        roles_permisos = {
            "Administrador": "ALL",  # Especial, asigna todos los permisos
            "Vendedor": [
                "ventas.crear", "ventas.ver",
                "clientes.crear", "clientes.ver"
            ],
            "Almacenero": [
                "productos.crear", "productos.ver", "productos.editar",
                "inventario.ver", "inventario.editar"
            ],
            "Cajero": [
                "ventas.crear", "ventas.ver", "gastos.ver", "gastos.crear"
            ],
            "Supervisor": [
                "reportes.ver", "reportes.exportar", "historial.ver"
            ],
            "Invitado": [
                "productos.ver", "clientes.ver"
            ]
        }

        # 4. Crear roles y asignar permisos
        for rol_nombre, permisos in roles_permisos.items():
            rol, creado = Role.objects.get_or_create(name=rol_nombre)
            if permisos == "ALL":
                rol.permissions.set(Permission.objects.all())
            else:
                rol.permissions.set([permisos_obj[perm] for perm in permisos if perm in permisos_obj])
            rol.save()
            self.stdout.write(
                self.style.SUCCESS(f"✔ Rol {'creado' if creado else 'actualizado'}: {rol_nombre}")
            )
