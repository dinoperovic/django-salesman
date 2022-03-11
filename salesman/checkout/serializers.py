from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

from salesman.conf import app_settings

from .payment import payment_methods_pool


class PaymentMethodSerializer(serializers.Serializer):
    """
    Serializer to display payment method with error.
    """

    identifier = serializers.CharField(read_only=True)
    label = serializers.CharField(read_only=True)
    error = serializers.CharField(allow_null=True, read_only=True)

    def to_representation(self, payment_method):
        data = super().to_representation(payment_method)
        payment = payment_methods_pool.get_payment(payment_method.identifier)
        request = self.context['request']
        try:
            if 'basket' in self.context:
                payment.validate_basket(basket=self.context['basket'], request=request)
            if 'order' in self.context:
                payment.validate_order(order=self.context['order'], request=request)
        except (ValidationError, DjangoValidationError) as e:
            error = serializers.as_serializer_error(e)
            data['error'] = error[api_settings.NON_FIELD_ERRORS_KEY][0]
        return data


class CheckoutSerializer(serializers.Serializer):
    """
    Serializer for processing a basket payment.
    """

    url = serializers.CharField(read_only=True)
    email = serializers.EmailField(write_only=True)
    shipping_address = serializers.CharField(
        allow_blank=True,
        write_only=True,
        style={'base_template': 'textarea.html'},
    )
    billing_address = serializers.CharField(
        allow_blank=True,
        write_only=True,
        style={'base_template': 'textarea.html'},
    )
    payment_method = serializers.ChoiceField(
        choices=payment_methods_pool.get_choices('basket'),
        write_only=True,
    )
    extra = serializers.JSONField(
        default=dict,
        write_only=True,
        help_text=_("Extra is updated and null values are removed."),
    )

    # Show payment methods with error on GET.
    payment_methods = PaymentMethodSerializer(many=True, read_only=True)

    def validate_shipping_address(self, value):
        context = self.context.copy()
        context['address'] = 'shipping'
        return app_settings.SALESMAN_ADDRESS_VALIDATOR(value, context=context)

    def validate_billing_address(self, value):
        context = self.context.copy()
        context['address'] = 'billing'
        return app_settings.SALESMAN_ADDRESS_VALIDATOR(value, context=context)

    def validate_payment_method(self, value):
        basket, request = self.context['basket'], self.context['request']
        payment = payment_methods_pool.get_payment(value)
        payment.validate_basket(basket, request)
        return payment

    def validate_extra(self, value):
        # Update basket `extra` instead of replacing it, remove null values.
        extra = self.context['basket'].extra
        if value:
            extra.update(value)
            extra = {k: v for k, v in extra.items() if v is not None}
        # Validate using extra validator.
        return app_settings.SALESMAN_EXTRA_VALIDATOR(extra, context=self.context)

    def save(self):
        basket, request = self.context['basket'], self.context['request']
        # Save extra data on basket.
        basket.extra = self.validated_data.get('extra', basket.extra)
        basket.extra['email'] = self.validated_data['email']
        basket.extra['shipping_address'] = self.validated_data['shipping_address']
        basket.extra['billing_address'] = self.validated_data['billing_address']
        basket.save(update_fields=['extra'])
        # Process the payment.
        payment = self.validated_data['payment_method']
        url = payment.basket_payment(basket, request)
        self.validated_data['url'] = url  # type: ignore
