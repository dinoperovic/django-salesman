from django.urls import include, path
from rest_framework.routers import DefaultRouter

from salesman.basket.api import BasketViewSet
from salesman.checkout.api import CheckoutViewSet
from salesman.checkout.payment import payment_methods_pool
from salesman.orders.api import OrderViewSet

router = DefaultRouter()
router.register('basket', BasketViewSet, basename='salesman-basket')
router.register('checkout', CheckoutViewSet, basename='salesman-checkout')
router.register('orders', OrderViewSet, basename='salesman-order')
urlpatterns = router.urls

# Add extra url patterns for payments defined in `PaymentMethod.get_urls()`.
for payment in payment_methods_pool.get_payments():
    urls = payment.get_urls()
    if urls:
        base_url = f'payment/{payment.identifier}/'
        urlpatterns.append(path(base_url, include(urls)))
