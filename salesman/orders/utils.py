from django.http import HttpRequest
from django.utils import timezone

from salesman.core.utils import get_salesman_model


def generate_ref(request: HttpRequest) -> str:
    """
    Default order reference generator function. Can be overriden by providing a
    dotted path to a function in ``SALESMAN_ORDER_REFERENCE_GENERATOR`` setting.

    Default format is ``{year}-{5-digit-increment}`` (eg. `2020-00001`).

    Args:
        request (HttpRequest): Django request

    Returns:
        str: New order reference
    """
    year = timezone.now().year
    Order = get_salesman_model('Order')
    last = Order.objects.filter(date_created__year=year, ref__isnull=False).first()
    increment = int(last.ref.split('-')[1]) + 1 if last and last.ref else 1
    return f'{year}-{increment:05d}'
