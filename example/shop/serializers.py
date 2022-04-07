# serializers.py
from rest_framework import serializers

from . import models


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ["name", "code"]


class PhoneVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PhoneVariant
        fields = ["name", "code", "color", "capacity"]
