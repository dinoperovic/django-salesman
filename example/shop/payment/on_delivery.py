# payment.py
from django.core.exceptions import ValidationError
from django.urls import reverse

from salesman.checkout.payment import PaymentMethod
from shop.models import Order


class PayOnDelivery(PaymentMethod):
    """
    Payment method that expects payment on delivery.
    """

    identifier = 'pay-on-delivery'
    label = 'Pay on delivery'

    def validate_basket(self, basket, request):
        """
        Payment only available when purchasing 10 items or less.
        """
        super().validate_basket(basket, request)
        if basket.quantity > 10:
            raise ValidationError("Can't pay for more than 10 items on delivery.")

    def basket_payment(self, basket, request):
        """
        Create order and mark it as shipped. Order status should be changed
        to `COMPLETED` and a new payment should be added manually by the merchant
        when the order items are received and paid for by the customer.
        """
        order = Order.objects.create_from_basket(basket, request, status='SHIPPED')
        basket.delete()
        url = reverse('salesman-order-last') + f'?token={order.token}'
        return request.build_absolute_uri(url)
