from django.core.exceptions import ValidationError as DjangoValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

from salesman.checkout.payment import payment_methods_pool
from salesman.checkout.serializers import PaymentMethodSerializer
from salesman.conf import app_settings
from salesman.core.serializers import PriceField
from salesman.core.utils import get_salesman_model

Order = get_salesman_model('Order')
OrderItem = get_salesman_model('OrderItem')
OrderPayment = get_salesman_model('OrderPayment')
OrderNote = get_salesman_model('OrderNote')


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for order item.
    """

    product = serializers.JSONField(source='product_data', read_only=True)
    unit_price = PriceField(read_only=True)
    subtotal = PriceField(read_only=True)
    total = PriceField(read_only=True)
    extra = serializers.JSONField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
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


class OrderPaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for order payment.
    """

    amount = PriceField(read_only=True)

    class Meta:
        model = OrderPayment
        fields = ['amount', 'transaction_id', 'payment_method', 'date_created']
        read_only_fields = fields


class OrderNoteSerializer(serializers.ModelSerializer):
    """
    Serializer for order note.
    """

    class Meta:
        model = OrderNote
        fields = ['message', 'date_created']
        read_only_fields = ['date_created']


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for order.
    """

    url = serializers.SerializerMethodField()
    subtotal = PriceField(read_only=True)
    total = PriceField(read_only=True)
    amount_paid = PriceField(read_only=True)
    amount_outstanding = PriceField(read_only=True)
    extra = serializers.JSONField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    payments = OrderPaymentSerializer(many=True, read_only=True)
    notes = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'url',
            'ref',
            'token',
            'status',
            'status_display',
            'date_created',
            'date_updated',
            'is_paid',
            'user',
            'email',
            'billing_address',
            'shipping_address',
            'subtotal',
            'extra_rows',
            'total',
            'amount_paid',
            'amount_outstanding',
            'extra',
            'items',
            'payments',
            'notes',
        ]
        read_only_fields = fields
        prefetch_related_fields = ['items', 'payments', 'notes']
        select_related_fields = ['user']

    def get_url(self, obj):
        request = self.context.get('request', None)
        url = reverse('salesman-order-detail', args=[obj.ref])
        return request.build_absolute_uri(url) if request else url

    def get_notes(self, obj):
        notes = [x for x in obj.notes.all() if x.public]
        return OrderNoteSerializer(notes, many=True).data


class StatusTransitionSerializer(serializers.Serializer):
    """
    Serializer to display order status with error.
    """

    value = serializers.CharField(read_only=True)
    label = serializers.CharField(read_only=True)
    error = serializers.CharField(allow_null=True, read_only=True)

    def to_representation(self, status):
        data = super().to_representation(status)
        order = self.context['order']
        try:
            app_settings.SALESMAN_ORDER_STATUS.validate_transition(status, order)
        except (ValidationError, DjangoValidationError) as e:
            error = serializers.as_serializer_error(e)
            data['error'] = error[api_settings.NON_FIELD_ERRORS_KEY][0]
        return data


class OrderStatusSerializer(serializers.ModelSerializer):
    """
    Serializer used to change order status.
    """

    status = serializers.ChoiceField(choices=app_settings.SALESMAN_ORDER_STATUS.choices)

    # Show status transitions with error on GET.
    status_transitions = StatusTransitionSerializer(
        source='Status',
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = ['status', 'status_display', 'status_transitions']

    def validate_status(self, status):
        order = self.context['order']
        return app_settings.SALESMAN_ORDER_STATUS.validate_transition(status, order)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context['request'].method == 'PUT' and 'status_transitions' in data:
            del data['status_transitions']
        return data


class OrderPaySerializer(serializers.Serializer):
    """
    Serializer used to pay for existing order via payment method.
    """

    payment_method = serializers.ChoiceField(
        choices=payment_methods_pool.get_choices('order'),
        write_only=True,
    )

    # Show payment methods with error on GET.
    payment_methods = PaymentMethodSerializer(many=True, read_only=True)

    def validate_payment_method(self, value):
        order, request = self.context['order'], self.context['request']
        payment = payment_methods_pool.get_payment(value)
        payment.validate_order(order, request)
        return payment

    def save(self):
        # Process the payment.
        order, request = self.context['order'], self.context['request']
        payment = self.validated_data['payment_method']
        data = payment.order_payment(order, request)
        # Returning string in payments converts to a URL data value.
        if isinstance(data, str):
            data = {'url': data}
        # Override the serializer data with the payment data.
        self._data = data


class OrderRefundSerializer(serializers.Serializer):
    """
    Serializer used to issue an order refund.
    """

    refunded = serializers.ListField(read_only=True)
    failed = serializers.ListField(read_only=True)

    def validate(self, attrs):
        order = self.context['order']
        if order.status == order.Status.REFUNDED:
            raise serializers.ValidationError(_("Order is already marked as Refunded."))
        return attrs

    def save(self):
        # Process the refund.
        order = self.context['order']
        refunded, failed = [], []
        for item in order.payments.all():
            payment = payment_methods_pool.get_payment(item.payment_method)
            serializer = OrderPaymentSerializer(item)
            if payment and payment.refund_payment(item):
                refunded.append(serializer.data)
            else:
                failed.append(serializer.data)
        # Set data and change order status.
        self.validated_data.update({'refunded': refunded, 'failed': failed})
        if not failed:
            order.status = order.Status.REFUNDED
            order.save(update_fields=['status'])
