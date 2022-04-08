from __future__ import annotations

from typing import Any

from django import forms

from salesman.conf import app_settings
from salesman.orders.models import BaseOrder

EMPTY_CHOICE = ("", "---------")


class OrderStatusSelect(forms.Select):
    """
    Status widget with order status choices.
    """

    # Bound by modelform.
    order: BaseOrder | None = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.choices = app_settings.SALESMAN_ORDER_STATUS.choices

    def create_option(
        self,
        name: str,
        value: str,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        option = super().create_option(name, value, *args, **kwargs)

        # Disable options that are not specified in status transitions.
        transitions = app_settings.SALESMAN_ORDER_STATUS.get_transitions()
        statuses = [status for status in app_settings.SALESMAN_ORDER_STATUS]
        current = self.order.status if self.order else ""
        if value != current and value not in transitions.get(current, statuses):
            option["attrs"]["disabled"] = True
        return option


class PaymentSelect(forms.Select):
    """
    Payment widget with payment method choices.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        from salesman.checkout.payment import payment_methods_pool

        super().__init__(*args, **kwargs)
        self.choices = [EMPTY_CHOICE] + payment_methods_pool.get_choices()
