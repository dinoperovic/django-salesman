from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.urls import URLPattern, URLResolver, include, path
from django.utils.translation import gettext_lazy as _

from salesman.conf import app_settings
from salesman.core.utils import get_salesman_model

if TYPE_CHECKING:  # pragma: no cover
    from salesman.basket.models import BaseBasket
    from salesman.orders.models import BaseOrder, BaseOrderPayment

Basket = get_salesman_model("Basket")
Order = get_salesman_model("Order")
OrderPayment = get_salesman_model("OrderPayment")


class PaymentError(Exception):
    """
    Payment error for raising payment related exceptions.
    """


class PaymentMethod:
    """
    Base payment method, all payment methods defined
    in ``SALESMAN_PAYMENT_METHODS`` must extend this class.
    """

    identifier: str
    label: str

    def get_urls(self) -> list[URLPattern | URLResolver]:
        """
        Hook for adding extra url patterns for payment method.
        Urls will be included as child patterns under the defined
        identifier namespace => ``/payment/{identifier}/{urls}``.
        """
        return []

    def is_enabled(self, request: HttpRequest) -> bool:
        """
        Method used to check that payment method is enabled for a given request.

        Args:
            request (HttpRequest): Django request

        Returns:
            bool: True if payment method is enabled
        """
        return True

    def validate_basket(self, basket: BaseBasket, request: HttpRequest) -> None:
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

    def validate_order(self, order: BaseOrder, request: HttpRequest) -> None:
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

        if order.status not in order.Status.get_payable():
            msg = _("Payment for order with status '{status}' is not allowed.")
            raise ValidationError(msg.format(status=order.status_display))

    def basket_payment(
        self,
        basket: BaseBasket,
        request: HttpRequest,
    ) -> str | dict[str, Any]:
        """
        This method gets called when new checkout is submitted and
        is responsible for creating a new order from given basket.

        Args:
            basket (Basket): Basket instance
            request (HttpRequest): Django request

        Raises:
            PaymentError: If error with payment occurs

        Returns:
            Union[str, dict]: Redirect URL string or JSON serializable data dictionary
        """
        raise NotImplementedError("Method `basket_payment()` is not implemented.")

    def order_payment(
        self,
        order: BaseOrder,
        request: HttpRequest,
    ) -> str | dict[str, Any]:
        """
        This method gets called when payment for an existing order is requested.

        Args:
            order (Order): Order instance
            request (HttpRequest): Django request

        Raises:
            PaymentError: If error with payment occurs

        Returns:
            Union[str, dict]: Redirect URL string or JSON serializable data dictionary
        """
        raise NotImplementedError("Method `order_payment()` is not implemented.")

    def refund_payment(self, payment: BaseOrderPayment) -> bool:
        """
        This method gets called when orders payment refund is requested.
        Should return True if refund was completed.

        Args:
            payment (OrderPayment): Order payment instance

        Returns:
            bool: True if refund was completed
        """
        return False


class PaymentMethodsPool:
    """
    Pool for storing payment method instances.
    """

    def __init__(self) -> None:
        self._payments: list[PaymentMethod] | None = None

    def get_payments(
        self,
        kind: str | None = None,
        request: HttpRequest = None,
    ) -> List[PaymentMethod]:
        """
        Returns payment method instances.

        Args:
            kind (Optional[str], optional): Either basket or order. Defaults to None.

        Returns:
            List[PaymentMethod]: Payment method instances
        """
        if not self._payments:
            self._payments = [P() for P in app_settings.SALESMAN_PAYMENT_METHODS]

        payments = self._payments
        if kind in ["basket", "order"]:
            method = f"{kind}_payment"
            payments = [p for p in payments if method in p.__class__.__dict__]
        if request:
            payments = [p for p in payments if p.is_enabled(request)]
        return payments

    def get_urls(self) -> list[URLPattern | URLResolver]:
        """
        Returns a list of url patterns for payments to be included.
        """
        urlpatterns: list[URLPattern | URLResolver] = []
        for payment in self.get_payments():
            urls = payment.get_urls()
            if urls:
                base_url = f"payment/{payment.identifier}/"
                urlpatterns.append(path(base_url, include(urls)))
        return urlpatterns

    def get_choices(
        self,
        kind: str | None = None,
        request: HttpRequest = None,
    ) -> list[tuple[str, str]]:
        """
        Return payments formated as choices list of tuples.

        Args:
            kind (Optional[str], optional): Either basket or order. Defaults to None.

        Returns:
            list: List of choices
        """
        return [(p.identifier, p.label) for p in self.get_payments(kind, request)]

    def get_payment(
        self,
        identifier: str,
        kind: str | None = None,
        request: HttpRequest = None,
    ) -> PaymentMethod | None:
        """
        Returns payment with given identifier.

        Args:
            identifier (str): Payment identifier
            kind (Optional[str], optional): Either basket or order. Defaults to None.

        Returns:
            PaymentMethod: Payment method instance
        """
        for payment in self.get_payments(kind, request):
            if payment.identifier == identifier:
                return payment
        return None


payment_methods_pool = PaymentMethodsPool()
