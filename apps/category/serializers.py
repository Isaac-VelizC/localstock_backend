from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.ReadOnlyField()
    parent_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'store', 'parent', 'parent_name', 'description',
            'slug', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'store']

    # Retorna el nombre del padre si existe, sino None
    def get_parent_name(self, obj):
        if obj.parent:
            return obj.parent.name
        return None
    
    def validate_name(self, value):
        if not all(char.isalpha() or char.isspace() for char in value):
            raise serializers.ValidationError("El nombre debe contener solo letras y espacios.")
        if len(value) < 2:
            raise serializers.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        store = getattr(user, 'store', None)
        if not store:
            raise serializers.ValidationError("El usuario no tiene una tienda asignada.")
        return Category.objects.create(store=store, **validated_data)

class CategoryParentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']