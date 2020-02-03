from decimal import Decimal
from typing import List, TypeVar

from django.http import HttpRequest

from salesman.conf import app_settings

from .models import Basket, BasketItem
from .serializers import ExtraRowSerializer

BasketOrItem = TypeVar('BasketOrItem', Basket, BasketItem)


class BasketModifier(object):
    """
    Basket modifier base, all modifiers defined
    in ``SALESMAN_BASKET_MODIFIERS`` must extend this class.
    """

    identifier = None

    def add_extra_row(
        self,
        obj: BasketOrItem,
        label: str,
        amount: Decimal,
        extra: dict = {},
        charge: bool = True,
    ) -> None:
        """
        Adds extra row to either the basket or item.

        Args:
            obj (BasketOrItem): Basket or BasketItem instance
            label (str): Row label
            amount (Decimal): Row amount
            extra (dict, optional): Row extra data. Defaults to {}.
            charge (bool, optional): Whether to charge the amount. Defaults to True.
        """
        instance = dict(label=label, amount=amount, extra=extra)
        obj.extra_rows[self.identifier] = ExtraRowSerializer(instance)
        if charge:
            obj.total += Decimal(amount)

    def process_item(self, item: BasketItem, request: HttpRequest) -> None:
        """
        Process item. Add extra row to item using ``self.add_extra_row()`` method.

        Args:
            item (BasketItem): Basket item instance
            request (HttpRequest): Django request
        """

    def process_basket(self, basket: Basket, request: HttpRequest) -> None:
        """
        Process basket. Add extra row to bakset using ``self.add_extra_row()`` method.

        Args:
            basket (Basket): Basket instance
            request (HttpRequest): Django request
        """


class BasketModifiersPool(object):
    """
    Pool for storing modifier instances.
    """

    _modifiers = None

    def get_modifiers(self) -> List[BasketModifier]:
        """
        Returns modifier instances.

        Returns:
            list: Modifier instances
        """
        if not self._modifiers:
            self._modifiers = [M() for M in app_settings.SALESMAN_BASKET_MODIFIERS]
        return self._modifiers


basket_modifiers_pool = BasketModifiersPool()
