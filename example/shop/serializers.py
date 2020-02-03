from rest_framework import serializers

from .models import PhoneVariant, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'code']


class PhoneVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneVariant
        fields = ['name', 'code', 'color', 'capacity']
