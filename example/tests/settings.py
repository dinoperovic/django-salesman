from ..project.settings import *  # noqa

SALESMAN_BASKET_MODIFIERS = [
    "shop.modifiers.DiscountModifier",
]
SALESMAN_PAYMENT_METHODS = [
    "tests.dummy.DummyPaymentMethod",
    "tests.dummy.DummyPaymentMethod2",
    "tests.dummy.DummyPaymentMethod3",
]

# Revert to defaults for testing
SALESMAN_ADDRESS_VALIDATOR = "salesman.checkout.utils.validate_address"
SALESMAN_PRICE_FORMATTER = "salesman.core.utils.format_price"
