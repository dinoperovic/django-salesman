from rest_framework.routers import DefaultRouter

from salesman.basket.views import BasketViewSet
from salesman.checkout.payment import payment_methods_pool
from salesman.checkout.views import CheckoutViewSet
from salesman.orders.views import OrderViewSet

router = DefaultRouter()
router.register('basket', BasketViewSet, basename='salesman-basket')
router.register('checkout', CheckoutViewSet, basename='salesman-checkout')
router.register('orders', OrderViewSet, basename='salesman-order')

urlpatterns = router.urls + payment_methods_pool.get_urls()
