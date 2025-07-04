from rest_framework import serializers
from .models import Rubro, Plan, Store, GeneralSetting

class RubroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rubro
        fields =  ['id', 'name']

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields =  ['id', 'name', 'price', 'max_users', 'max_products', 'features']

class StoreUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['name', 'country']

    def validate(self, attrs):
        store = self.instance
        if store and store.plan and store.plan.name.lower() in ['básico']:
            campos_restringidos = ['logo']
            for campo in campos_restringidos:
                if campo in attrs and getattr(store, campo) != attrs[campo]:
                    raise serializers.ValidationError({
                        campo: f"No puedes modificar este campo con el plan '{store.plan.name}'."
                    })
        return attrs

class GeneralSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralSetting
        fields = [
            'timezone', 'idioma', 'currency', 'tax_enabled',
            'alerts_stock', 'stock_minimo', 'notification_email',
            'auto_update_price_on_purchase', 'margin_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['store']

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            'id', 'name', 'code', 'logo', 'rubro', 
            'plan', 'country', 'created_at', 'updated_at'
        ]