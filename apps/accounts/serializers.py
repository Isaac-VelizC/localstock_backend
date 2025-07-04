from rest_framework import serializers
from .models import User, Role, Permission
from apps.stores.models import Store, GeneralSetting, Plan, Rubro
from apps.warehouse.models import Warehouse, UserWarehouseAccess
import random
import string

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields =  ['id', 'name']

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields =  ['id', 'name', 'module', 'action', 'slug']

class AccountSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='role.name', read_only=True)
    name_store = serializers.CharField(source='store.name', read_only=True)
    rubro = serializers.SerializerMethodField()
    currency = serializers.CharField(source='store.settings.currency', read_only=True)
    country = serializers.CharField(source='store.country', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'name', 'surnames', 'email', 'phone',
            'role', 'store', 'name_store', 'rubro',
            'country', 'currency', 'owner', 'is_active', 'completed_Onboarding', 'is_staff'
        ]

    def get_rubro(self, obj):
        rubro = obj.store.rubro
        return rubro.name if rubro else None

class AccountUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [ 'username', 'name', 'surnames', 'email', 'phone' ]
        read_only_fields = ['id', 'role', 'store', 'owner', 'is_active', 'completed_Onboarding', 'is_staff']

class RegisterUserSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'name', 'surnames', 'email', 'username', 'phone', 'password', 'store_name']
        read_only_fields = ['id', 'role', 'name', 'surnames', 'phone', 'store']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value
    
    def generate_warehouse_code(self, length=6):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if not Warehouse.objects.filter(code=code).exists():
                return code
    
    def generate_store_code(self, length=4):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if not Store.objects.filter(code=code).exists():
                return code
    
    def create(self, validated_data):
        # Extraer el nombre del correo electrónico
        email = validated_data['email']
        username_part = email.split('@')[0]
        name_parts = username_part.replace('-', '.').split('.')  # Permite separar si usan '-' o '.'

        name = name_parts[0].capitalize()
        surname = name_parts[1].capitalize() if len(name_parts) > 1 else ''

        # Crear la tienda
        plan = Plan.objects.get(name="Básico")
        store = Store.objects.create(
            name=validated_data['store_name'],
            code = self.generate_store_code(),
            plan=plan,
            rubro=None,
            logo=None,
        )

        # Crear configuración general por defecto
        GeneralSetting.objects.get_or_create(store=store)
        # Crear almacen principal por defecto
        warehouse = Warehouse.objects.create(
            name = f'Almacén principal - {store.name}',
            code = self.generate_warehouse_code(),
            store = store
        )
        # Rol por defecto
        admin_role, _ = Role.objects.get_or_create(name="Administrador")
        # Crear el usuario
        user = User.objects.create(
            username=username_part,
            name=name,
            surnames=surname,
            email=validated_data['email'],
            password=validated_data['password'],
            role = admin_role,
            store=store,
            owner=True
        )

        # Asignar acceso al almacén principal
        UserWarehouseAccess.objects.create(
            user=user,
            warehouse=warehouse,
            role=admin_role,
            is_default=True
        )

        return user
    
class UserOnboardingSerializer(serializers.Serializer):
    name_store = serializers.CharField(max_length=100)
    rubro = serializers.PrimaryKeyRelatedField(queryset=Rubro.objects.all())
    name = serializers.CharField(max_length=100)
    surnames = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)
    country = serializers.CharField(max_length=3)   # ISO 3166
    currency = serializers.CharField(max_length=10)

    def validate_currency(self, value):
        allowed = ['BOB', 'ARS', 'CLP', 'COP', 'USD', 'MXN', 'PYG', 'PEN', 'UYU', 'VES']
        if value not in allowed:
            raise serializers.ValidationError("Moneda no permitida.")
        return value

    def update(self, user, validated_data):
        store = user.store
        if not store:
            raise serializers.ValidationError("El usuario no tiene tienda asignada.")

        # Actualizar tienda
        store.name = validated_data['name_store']
        store.rubro = validated_data['rubro']
        store.country = validated_data['country']
        store.save()

        # Actualizar configuración general
        general_setting, _ = GeneralSetting.objects.get_or_create(store=store)
        general_setting.currency = validated_data['currency']
        general_setting.save()

        # Actualizar usuario
        user.name = validated_data['name']
        user.surnames = validated_data['surnames']
        user.phone = validated_data['phone']
        user.completed_Onboarding = True
        user.save()

        return user

