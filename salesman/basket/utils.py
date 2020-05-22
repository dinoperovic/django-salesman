from django.core.exceptions import ValidationError  # noqa


def validate_extra(value: dict, context: dict) -> dict:
    """
    Default extra validator function. Can be overriden by providing a
    dotted path to a function in ``SALESMAN_EXTRA_VALIDATOR`` setting.

    Args:
        value (str): Extra dict to be validated
        context (dict, optional): Validator context data.

    Raises:
        ValidationError: In case data is not valid

    Returns:
        dict: Validated value
    """
    return value
