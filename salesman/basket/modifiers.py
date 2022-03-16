from decimal import Decimal
from typing import List, Optional, Union

from django.http import HttpRequest

from salesman.conf import app_settings

from .models import BaseBasket, BaseBasketItem
from .serializers import ExtraRowSerializer


class BasketModifier:
    """
    Basket modifier used to process the basket on every request.
    Modifier methods get called in top-to-bottom order as defined in this class.

    All modifiers defined in ``SALESMAN_BASKET_MODIFIERS`` must extend this class.
    """

    identifier: str

    def setup_basket(self, basket: BaseBasket, request: HttpRequest) -> None:
        """
        Initial modifier Basket setup before any processing.

        Args:
            basket (BaseBasket): Basket instance
            request (HttpRequest): Django request
        """

    def setup_item(self, item: BaseBasketItem, request: HttpRequest) -> None:
        """
        Initial modifier Basket item setup before any processing.

        Args:
            basket (BaseBasket): Basket instance
            request (HttpRequest): Django request
        """

    def process_item(self, item: BaseBasketItem, request: HttpRequest) -> None:
        """
        Process item. Add extra row to item using ``self.add_extra_row()`` method.

        Args:
            item (BasketItem): Basket item instance
            request (HttpRequest): Django request
        """

    def finalize_item(self, item: BaseBasketItem, request: HttpRequest) -> None:
        """
        Finalize item after after all items were already processed.

        Args:
            item (BaseBasketItem): Basket item instance
            request (HttpRequest): Django request
        """

    def process_basket(self, basket: BaseBasket, request: HttpRequest) -> None:
        """
        Process basket. Add extra row to bakset using ``self.add_extra_row()`` method.

        Args:
            basket (Basket): Basket instance
            request (HttpRequest): Django request
        """

    def finalize_basket(self, basket: BaseBasket, request: HttpRequest) -> None:
        """
        Finalize basket after after all items and basket were already processed.

        Args:
            item (BaseBasketItem): Basket instance
            request (HttpRequest): Django request
        """

    def add_extra_row(
        self,
        obj: Union[BaseBasket, BaseBasketItem],
        request: HttpRequest,
        label: str,
        amount: Decimal,
        extra: dict = {},
        charge: bool = True,
        identifier: Optional[str] = None,
    ) -> None:
        """
        Adds extra row to either the basket or item.

        Args:
            obj (BasketOrItem): Basket or BasketItem instance
            request (HttpRequest): Django request
            label (str): Row label
            amount (Decimal): Row amount
            extra (dict, optional): Row extra data. Defaults to {}.
            charge (bool, optional): Whether to charge the amount. Defaults to True.
            identifier (Optional[str], optional): Extra row ID. Defaults to modifier ID.
        """
        if not identifier:
            identifier = self.identifier

        instance = {'label': label, 'amount': amount, 'extra': extra}
        context = {'request': request}
        obj.extra_rows[identifier] = ExtraRowSerializer(instance, context=context)
        if charge:
            obj.total += Decimal(amount)


class BasketModifiersPool:
    """
    Pool for storing modifier instances.
    """

    def __init__(self):
        self._modifiers: Optional[list[BasketModifier]] = None

    def get_modifiers(self) -> List[BasketModifier]:
        """
        Returns modifier instances.

        Returns:
            list: Modifier instances
        """
        if self._modifiers is None:
            self._modifiers = [M() for M in app_settings.SALESMAN_BASKET_MODIFIERS]
        return self._modifiers


basket_modifiers_pool = BasketModifiersPool()
