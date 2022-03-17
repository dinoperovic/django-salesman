from decimal import Decimal
from typing import Protocol, runtime_checkable

from django.db.models.options import Options
from django.http import HttpRequest


@runtime_checkable
class Product(Protocol):
    """
    Product protocol that all Salesman product models should implement.
    """

    id: int
    name: str
    code: str

    # Django model attribute.
    _meta: Options

    def get_price(self, request: HttpRequest) -> Decimal:
        """
        Method that returns product price for the given request.

        Args:
            request (HttpRequest): Django request

        Returns:
            Decimal: Product price
        """
