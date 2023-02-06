# payment.py
from django.urls import reverse

from salesman.checkout.payment import PaymentMethod
from shop.models import Order


class AdminPayment(PaymentMethod):
    """
    Payment method for admin orders.
    """

    identifier = "admin-payment"
    label = "Admin payment"

    def is_enabled(self, request):
        """
        Only enabled for staff admin users.
        """
        return request.user.is_staff

    def get_order_url(self, order, request):
        """
        Return order url with token.
        """
        url = reverse("salesman-order-last") + f"?token={order.token}"
        return request.build_absolute_uri(url)

    def add_order_admin_payment(self, order, request):
        """
        Mark order as payed.
        """
        order.pay(order.total, f"admin-{request.user.id}-{order.ref}", self.identifier)

    def basket_payment(self, basket, request):
        """
        Create a payed order and mark it as completed.
        """
        order = Order.objects.create_from_basket(basket, request, status="COMPLETED")
        self.add_order_admin_payment(order, request)
        basket.delete()
        return self.get_order_url(order, request)

    def order_payment(self, order, request):
        """
        Mark order as payed.
        """
        order.status = "COMPLETED"
        order.save(update_fields=["status"])
        self.add_order_admin_payment(order, request)
        return self.get_order_url(order, request)
