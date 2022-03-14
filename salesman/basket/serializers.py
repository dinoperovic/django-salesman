from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from salesman.basket.models import BaseBasketItem
from salesman.conf import app_settings
from salesman.core.serializers import PriceField
from salesman.core.utils import get_salesman_model

Basket = get_salesman_model('Basket')
BasketItem = get_salesman_model('BasketItem')


class ProductField(serializers.DictField):
    """
    Related product field that uses a serializer based on product type
    taken from ``SALESMAN_PRODUCT_TYPES`` setting.
    """

    def to_representation(self, product, request=None):
        product_types = app_settings.SALESMAN_PRODUCT_TYPES
        serializer_class = product_types[product._meta.label]
        return serializer_class(context=self.context).to_representation(product)


class ExtraRowsField(serializers.ListField):
    """
    Field to display a list of ``ExtraRowSerializer`` instances.
    """

    def to_representation(self, rows):
        return [dict(row.data, modifier=modifier) for modifier, row in rows.items()]


class ExtraRowSerializer(serializers.Serializer):
    """
    Extra row serializer used for adding extra data to ``extra_rows`` dict on
    both the basket and basket item model. Mostly used when processing basket modifiers.
    """

    label = serializers.CharField(read_only=True, default="")
    amount = PriceField(read_only=True, default=0)
    extra = serializers.DictField(read_only=True, default={})


class BasketItemSerializer(serializers.ModelSerializer):
    """
    Serializer for basket item.
    """

    url = serializers.SerializerMethodField()
    product_type = serializers.CharField(source='product._meta.label', read_only=True)
    product = ProductField(read_only=True)
    quantity = serializers.IntegerField(min_value=1)
    unit_price = PriceField(read_only=True)
    subtotal = PriceField(read_only=True)
    extra_rows = ExtraRowsField(read_only=True)
    total = PriceField(read_only=True)
    extra = serializers.JSONField(
        default=dict, help_text=_("Extra is updated and null values are removed.")
    )

    class Meta:
        model = BasketItem
        fields = [
            'url',
            'ref',
            'product_type',
            'product_id',
            'product',
            'unit_price',
            'quantity',
            'subtotal',
            'extra_rows',
            'total',
            'extra',
        ]
        read_only_fields = fields

    def get_url(self, obj):
        request = self.context.get('request', None)
        url = reverse('salesman-basket-detail', args=[obj.ref])
        return request.build_absolute_uri(url) if request else url

    def validate(self, attrs):
        context = self.context.copy()
        context['basket_item'] = self.instance
        return app_settings.SALESMAN_BASKET_ITEM_VALIDATOR(attrs, context=context)

    def validate_extra(self, value):
        # Update basket `extra` instead of replacing it, remove null values.
        extra = self.instance.extra if self.instance else {}
        if value:
            extra.update(value)
            extra = {k: v for k, v in extra.items() if v is not None}

        # Validate using extra validator.
        context = self.context.copy()
        context['basket_item'] = self.instance
        return app_settings.SALESMAN_EXTRA_VALIDATOR(extra, context=context)

    def to_representation(self, item):
        basket, request = self.context['basket'], self.context['request']
        basket.update(request)
        item = basket.find(item.ref)
        return super().to_representation(item)


class BasketItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer used to add a new item to basket.
    """

    ref = serializers.SlugField(
        required=False, help_text=_("Leave empty to auto-generate from product.")
    )
    product_type = serializers.ChoiceField(
        choices=list(app_settings.SALESMAN_PRODUCT_TYPES)
    )
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(default=1, min_value=1)
    extra = serializers.JSONField(default=dict, help_text=_("Store extra JSON data."))

    class Meta:
        model = BasketItem
        fields = ['ref', 'product_type', 'product_id', 'quantity', 'extra']

    def validate(self, attrs):
        # Validate and set product from generic relation.
        app_label, model_name = attrs['product_type'].split('.')
        model = apps.get_model(app_label, model_name)
        content_type = ContentType.objects.get_for_model(model)
        try:
            pid = attrs['product_id']
            attrs['product'] = content_type.get_object_for_this_type(id=pid)
        except ObjectDoesNotExist:
            msg = _("Product '{product_type}' with id '{product_id}' doesn't exist.")
            raise serializers.ValidationError(msg.format(**attrs))

        # Validate using basket item validator.
        context = self.context.copy()
        context['basket_item'] = self.instance
        return app_settings.SALESMAN_BASKET_ITEM_VALIDATOR(attrs, context=context)

    def validate_extra(self, value):
        context = self.context.copy()
        context['basket_item'] = self.instance
        return app_settings.SALESMAN_EXTRA_VALIDATOR(value, context=context)

    def create(self, validated_data) -> BaseBasketItem:
        basket = self.context['basket']
        return basket.add(
            product=validated_data['product'],
            quantity=validated_data['quantity'],
            ref=validated_data.get('ref', None),
            extra=validated_data.get('extra', None),
        )

    def to_representation(self, item):
        return BasketItemSerializer(context=self.context).to_representation(item)


class BasketSerializer(serializers.ModelSerializer):
    """
    Serializer for basket.
    """

    items = BasketItemSerializer(source='get_items', many=True, read_only=True)
    subtotal = PriceField(read_only=True)
    extra_rows = ExtraRowsField(read_only=True)
    total = PriceField(read_only=True)
    extra = serializers.JSONField(read_only=True)

    class Meta:
        model = Basket
        fields = ['id', 'items', 'subtotal', 'extra_rows', 'total', 'extra']

    def to_representation(self, basket):
        basket.update(self.context['request'])
        return super().to_representation(basket)


class BasketExtraSerializer(serializers.ModelSerializer):
    """
    Serializer for updating basket ``extra`` data.
    """

    extra = serializers.JSONField(
        help_text=_("Extra is updated and null values are removed.")
    )

    class Meta:
        model = Basket
        fields = ['extra']

    def validate_extra(self, value):
        # Update basket extra instead of replacing it, remove null values.
        extra = self.instance.extra if self.instance else {}
        if value:
            extra.update(value)
            extra = {k: v for k, v in extra.items() if v is not None}
        # Validate using extra validator.
        return app_settings.SALESMAN_EXTRA_VALIDATOR(extra, context=self.context)
