# utils.py


def custom_address_validator(value, context):
    """
    Address not required at all for this example,
    skip default (required) validation.
    """
    return value


def custom_price_format(value, context):
    """
    Force a fixed dollar currency.
    """
    return f"${value:.2f}"
