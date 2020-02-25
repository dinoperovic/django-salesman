from typing import List, Optional

from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.urls import include, path
from django.utils.translation import gettext_lazy as _

from salesman.basket.models import Basket
from salesman.conf import app_settings
from salesman.orders.models import Order, OrderPayment


class PaymentError(Exception):
    """
    Payment error for raising payment related exceptions.
    """


class PaymentMethod(object):
    """
    Base payment method, all payment methods defined
    in ``SALESMAN_PAYMENT_METHODS`` must extend this class.
    """

    identifier = None
    label = None

    def get_urls(self) -> list:
        """
        Hook for adding extra url patterns for payment method.
        Urls will be included as child patterns under the defined
        identifier namespace => ``/payment/{identifier}/{urls}``.
        """
        return []

    def validate_basket(self, basket: Basket, request: HttpRequest) -> None:
        """
        Method used to validate that payment method is valid for the given basket.

        Args:
            basket (Basket): Basket instance
            request (HttpRequest): Django request

        Raises:
            ValidationError: If payment is not valid for basket
        """
        if not basket.count:
            raise ValidationError(_("Your basket is empty."))

    def validate_order(self, order: Order, request: HttpRequest) -> None:
        """
        Method used to validate that payment method is valid for the given order.

        Args:
            order (Order): Order instance
            request (HttpRequest): Django request

        Raises:
            ValidationError: If payment is not valid for order
        """
        if order.is_paid:
            raise ValidationError(_("This order has already been paid for."))

        if order.status not in order.statuses.get_payable():
            msg = _("Payment for order with status '{status}' is not allowed.")
            raise ValidationError(msg.format(status=order.status_display))

    def basket_payment(self, basket: Basket, request: HttpRequest) -> str:
        """
        This method gets called when new checkout is submitted and
        is responsible for creating a new order from given basket.
        Should return the redirect url to either the next payment step or
        the order success page. Raise ``PaymentError`` in case an issue appears.

        Args:
            basket (Basket): Basket instance
            request (HttpRequest): Django request

        Raises:
            PaymentError: If error with payment occurs

        Returns:
            str: Redirect url to the next step
        """
        raise NotImplementedError("Method `basket_payment()` is not implemented.")

    def order_payment(self, order: Order, request: HttpRequest) -> str:
        """
        This method gets called when payment for an existing order is requested.
        Should return the redirect url to either the next payment step or the
        order success page. Raise ``PaymentError`` in case an issue appears.

        Args:
            order (Order): Order instance
            request (HttpRequest): Django request

        Raises:
            PaymentError: If error with payment occurs

        Returns:
            str: Redirect url to the next step
        """
        raise NotImplementedError("Method `order_payment()` is not implemented.")

    def refund_payment(self, payment: OrderPayment) -> bool:
        """
        This method gets called when orders payment refund is requested.
        Should return True if refund was completed.

        Args:
            payment (OrderPayment): Order payment instance

        Returns:
            bool: True if refund was completed
        """
        return False


class PaymentMethodsPool(object):
    """
    Pool for storing payment method instances.
    """

    _payments = None

    def get_payments(self, kind: Optional[str] = None) -> List[PaymentMethod]:
        """
        Returns payment method instances.

        Args:
            kind (Optional[str], optional): Either basket or order. Defaults to None.

        Returns:
            List[PaymentMethod]: Payment method instances
        """
        if not self._payments:
            self._payments = [P() for P in app_settings.SALESMAN_PAYMENT_METHODS]
        if kind in ['basket', 'order']:
            method = f'{kind}_payment'
            return [p for p in self._payments if method in p.__class__.__dict__]
        return self._payments

    def get_urls(self) -> list:
        """
        Returns a list of url patterns for payments to be included.
        """
        urlpatterns = []
        for payment in self.get_payments():
            urls = payment.get_urls()
            if urls:
                base_url = f'payment/{payment.identifier}/'
                urlpatterns.append(path(base_url, include(urls)))
        return urlpatterns

    def get_choices(self, kind: Optional[str] = None) -> list:
        """
        Return payments formated as choices list of tuples.

        Args:
            kind (Optional[str], optional): Either basket or order. Defaults to None.

        Returns:
            list: List of choices
        """
        return [(p.identifier, p.label) for p in self.get_payments(kind=kind)]

    def get_payment(self, identifier: str, kind: Optional[str] = None) -> PaymentMethod:
        """
        Returns payment with given identifier.

        Args:
            identifier (str): Payment identifier
            kind (Optional[str], optional): Either basket or order. Defaults to None.

        Returns:
            PaymentMethod: Payment method instance
        """
        for payment in self.get_payments(kind=kind):
            if payment.identifier == identifier:
                return payment


payment_methods_pool = PaymentMethodsPool()
