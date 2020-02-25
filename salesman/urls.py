from rest_framework.routers import DefaultRouter

from salesman.basket.api import BasketViewSet
from salesman.checkout.api import CheckoutViewSet
from salesman.checkout.payment import payment_methods_pool
from salesman.orders.api import OrderViewSet

router = DefaultRouter()
router.register('basket', BasketViewSet, basename='salesman-basket')
router.register('checkout', CheckoutViewSet, basename='salesman-checkout')
router.register('orders', OrderViewSet, basename='salesman-order')

urlpatterns = router.urls + payment_methods_pool.get_urls()
