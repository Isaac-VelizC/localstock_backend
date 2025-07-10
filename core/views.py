
from django.core import management
from django.http import JsonResponse


def deploy_migrate(request):
    management.call_command('migrate')
    management.call_command('collectstatic', interactive=False)
    return JsonResponse({'status': 'OK'})