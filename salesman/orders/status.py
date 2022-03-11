from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:  # pragma: no cover
    from salesman.orders.models import BaseOrder


class BaseOrderStatus(models.TextChoices):
    """
    Base order status enum, actuall choices must extend this class.
    """

    @classmethod
    def get_payable(cls) -> list[str]:
        """
        Returns list of statuses from which an order is eligible for payment.
        """
        return []

    @classmethod
    def get_transitions(cls) -> dict[str, list[str]]:
        """
        Returns a dict of statuses with their transitions.
        If not specified for status, any transition is valid.
        """
        return {}

    @classmethod
    def validate_transition(cls, status: str, order: BaseOrder) -> str:
        """
        Validate a given status transition for the order.
        By default check status is defined in transitions.

        Args:
            status (str): New status
            order (Order): Order instance

        Raises:
            ValidationError: If transition not valid

        Returns:
            str: Validated status
        """
        transitions = cls.get_transitions().get(order.status, [status])
        transitions.append(order.status)
        if status not in transitions:
            current, new = cls[order.status].label, cls[status].label  # type: ignore
            msg = _(f"Can't change order with status '{current}' to '{new}'.")
            raise ValidationError(msg)
        return status


class OrderStatus(BaseOrderStatus):
    """
    Default order choices enum. Can be overriden by providing a
    dotted path to a class in ``SALESMAN_ORDER_STATUS`` setting.
    Required choices are NEW, CREATED, COMPLETED and REFUNDED.
    """

    NEW = 'NEW', _("New")  # Order with reference created, items are in the basket.
    CREATED = 'CREATED', _("Created")  # Created with items and pending payment.
    HOLD = 'HOLD', _("Hold")  # Stock reduced but still awaiting payment.
    FAILED = 'FAILED', _("Failed")  # Payment failed, retry is available.
    CANCELLED = 'CANCELLED', _("Cancelled")  # Cancelled by seller, stock increased.
    PROCESSING = 'PROCESSING', _("Processing")  # Payment confirmed, processing order.
    SHIPPED = 'SHIPPED', _("Shipped")  # Shipped to customer.
    COMPLETED = 'COMPLETED', _("Completed")  # Completed and received by customer.
    REFUNDED = 'REFUNDED', _("Refunded")  # Fully refunded by seller.

    @classmethod
    def get_payable(cls) -> list:
        """
        Returns default payable statuses.
        """
        return [cls.CREATED, cls.HOLD, cls.FAILED]

    @classmethod
    def get_transitions(cls) -> dict:
        """
        Returns default status transitions.
        """
        return {
            'NEW': [cls.CREATED],
            'CREATED': [cls.HOLD, cls.FAILED, cls.CANCELLED, cls.PROCESSING],
            'HOLD': [cls.FAILED, cls.CANCELLED, cls.PROCESSING],
            'FAILED': [cls.CANCELLED, cls.PROCESSING],
            'CANCELLED': [],
            'PROCESSING': [cls.SHIPPED, cls.COMPLETED, cls.REFUNDED],
            'SHIPPED': [cls.COMPLETED, cls.REFUNDED],
            'COMPLETED': [cls.REFUNDED],
            'REFUNDED': [],
        }
