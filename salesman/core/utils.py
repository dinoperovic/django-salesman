from decimal import Decimal


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
