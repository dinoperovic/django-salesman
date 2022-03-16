from django.urls import path

from salesman.checkout.payment import PaymentError, PaymentMethod
from salesman.core.utils import get_salesman_model

Order = get_salesman_model('Order')


class DummyPaymentMethod(PaymentMethod):
    identifier = 'dummy'
    label = 'Dummy'

    def get_urls(self):
        return [
            path('dummy-url/', self.dummy_view, name='dummy-url'),
        ]

    def basket_payment(self, basket, request):
        if 'raise_error' in basket.extra:
            raise PaymentError("Dummy payment error")
        # create order
        Order.objects.create_from_basket(basket, request)
        return '/success/'

    def order_payment(self, order, request):
        if 'raise_error' in request.GET:
            raise PaymentError("Dummy payment error")
        return '/success/'

    def dummy_view(self, request):
        pass


class DummyPaymentMethod2(DummyPaymentMethod):
    identifier = 'dummy2'
    label = 'Dummy 2'

    def refund_payment(self, payment):
        return True


class DummyPaymentMethod3(DummyPaymentMethod):
    identifier = 'dummy3'
    label = 'Dummy 3'

    def order_payment(self, order, request):
        return '/success/'
