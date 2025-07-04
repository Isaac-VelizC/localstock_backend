from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from .serializers import StoreSerializer, GeneralSettingSerializer, RubroSerializer, StoreUpdateSerializer
from .models import Store, Plan, Rubro, GeneralSetting
from rest_framework.request import Request
from django_countries import countries

# Create your views here.
class RubroListView(generics.ListAPIView):
    queryset = Rubro.objects.all()
    serializer_class = RubroSerializer
    permission_classes = [permissions.IsAuthenticated]

class StoreConfigView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            store = request.user.store
            settings = store.settings
        except Store.DoesNotExist:
            raise NotFound('No se encontró la tienda del usuario.')
        except GeneralSetting.DoesNotExist:
            raise NotFound('No se encontraron los ajustes generales.')

        store_data = StoreSerializer(store).data
        settings_data = GeneralSettingSerializer(settings).data

        return Response({
            "store": store_data,
            "settings": settings_data
        })

    def put(self, request):
        try:
            store = request.user.store
            settings = store.settings
        except Store.DoesNotExist:
            raise NotFound('No se encontró la tienda del usuario.')
        except AttributeError:
            raise NotFound('No se encontraron los ajustes generales.')
                
        store_data = request.data.get('store', {})
        settings_data = request.data.get('settings', {})

        # Serializers individuales
        store_serializer = StoreUpdateSerializer(store, data=store_data, partial=True)
        settings_serializer = GeneralSettingSerializer(settings, data=settings_data, partial=True)

        store_serializer.is_valid(raise_exception=True)
        settings_serializer.is_valid(raise_exception=True)

        store_serializer.save()
        settings_serializer.save()

        return Response({
            'store': store_serializer.data,
            'settings': settings_serializer.data
        })

# Cambio de Plan temporal
class ChangePlanTemporaryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        plan_id = request.data.get('plan_id')
        try:
            plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            return Response({"error": "Plan no válido."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            store = Store.objects.get(user=request.user)
        except Store.DoesNotExist:
            return Response({"error": "Tienda no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        store.plan = plan
        store.save()
        return Response({"message": f"Plan cambiado a {plan.name}."}, status=status.HTTP_200_OK)

class CountryListView(APIView):
    def get(self, request: Request):
        search_term = request.GET.get('search', '').lower()

        AMERICAS = {
            'AR', 'BO', 'BR', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'SV', 'GT',
            'GY', 'HT', 'HN', 'JM', 'MX', 'NI', 'PA', 'PY', 'PE', 'PR', 'SR',
            'TT', 'UY', 'VE', 'US', 'CA', 'BZ', 'BS', 'BB', 'AG', 'LC', 'GD',
            'DM', 'KN', 'VC'
        }

        result = [
            {"code": code, "name": name}
            for code, name in countries
            if code in AMERICAS and (
                search_term in name.lower() or search_term in code.lower()
            )
        ]

        result.sort(key=lambda c: c["name"])

        return Response(result)
