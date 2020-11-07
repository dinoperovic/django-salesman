from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_address(value: str, context: dict = {}) -> str:
    """
    Default address validator function. Can be overriden by providing a
    dotted path to a function in ``SALESMAN_ADDRESS_VALIDATOR`` setting.

    Args:
        value (str): Address text to be validated
        context (dict, optional): Validator context data.

    Raises:
        ValidationError: In case address is not valid

    Returns:
        str: Validated value
    """
    if not value:
        raise ValidationError(_("Address is required."))
    return value
