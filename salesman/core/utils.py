from decimal import Decimal

from django.apps import apps
from django.db.models import Model

from salesman.conf import app_settings


def format_price(value: Decimal, context: dict = {}) -> str:
    """
    Default price format function. Can be overriden by providing a
    dotted path to a function in ``SALESMAN_PRICE_FORMATTER`` setting.

    Args:
        value (Decimal): Number value to be formatted
        context (dict, optional): Format context data. Defaults to {}.

    Returns:
        str: Formatted price as a string
    """
    return f'{value:.2f}'


def get_salesman_model(name: str) -> Model:
    """
    Loads and returns a Salesman model by name.
    Should be used for accessing all models to allow for swappable models.

    Args:
        name (str): A camel case Salesman model name

    Returns:
        type: Model class
    """
    setting = "".join(["_" + x if x.isupper() else x for x in name]).lstrip("_").upper()
    setting = f"SALESMAN_{setting}_MODEL"

    try:
        value = getattr(app_settings, setting)
    except AttributeError:
        raise ValueError(f"Model `{name}` is not a valid Salesman model.")

    return apps.get_model(value)
