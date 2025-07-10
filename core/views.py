
from django.core import management
from django.http import JsonResponse
from django.contrib.auth import get_user_model

def deploy_all(request):
    try:
        management.call_command('migrate')
        management.call_command('collectstatic', interactive=False)
        management.call_command('seed_all')

        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@admin.com', 'Admin*1234')
            superuser_status = "Superusuario creado: admin"
        else:
            superuser_status = "Superusuario ya existe."

        return JsonResponse({
            'status': '✅ Todo ejecutado correctamente',
            'superuser': superuser_status
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
