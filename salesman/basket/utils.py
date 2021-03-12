from django.core.exceptions import ValidationError  # noqa


def validate_basket_item(attrs: dict, context: dict = {}) -> dict:
    """
    Default basket item validator function. Can be overrider by providing
    a path to a function in ``SALESMAN_BASKET_ITEM_VALIDATOR`` setting.

    Args:
        attrs (dict): Attributes to be validated.
        context (dict, optional): Validator context data. Defaults to {}.

    Raises:
        ValidationError: In case data is not valid

    Returns:
        dict: Validated attrs
    """
    return attrs


def validate_extra(value: dict, context: dict = {}) -> dict:
    """
    Default extra validator function. Can be overriden by providing a
    dotted path to a function in ``SALESMAN_EXTRA_VALIDATOR`` setting.

    Args:
        value (str): Extra dict to be validated
        context (dict, optional): Validator context data. Defaults to {}.

    Raises:
        ValidationError: In case data is not valid

    Returns:
        dict: Validated value
    """
    return value
