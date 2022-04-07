import pytest
from django.core.exceptions import ImproperlyConfigured

from salesman.basket.modifiers import BasketModifier
from salesman.checkout.payment import PaymentMethod
from salesman.conf import app_settings
from salesman.orders.status import BaseOrderStatus
from shop.models import InvalidProduct


@pytest.mark.django_db
def test_product_types(settings):
    assert app_settings.SALESMAN_PRODUCT_TYPES["shop.Product"]
    del app_settings.SALESMAN_PRODUCT_TYPES
    with pytest.raises(ImproperlyConfigured):
        # invalid path
        settings.SALESMAN_PRODUCT_TYPES = {"invalid.Invalid": None}
        assert app_settings.SALESMAN_PRODUCT_TYPES
        del app_settings.SALESMAN_PRODUCT_TYPES
    with pytest.raises(ImproperlyConfigured):
        # invalid serializer
        settings.SALESMAN_PRODUCT_TYPES = {"shop.Product": "invalid.Serializer"}
        assert app_settings.SALESMAN_PRODUCT_TYPES
        del app_settings.SALESMAN_PRODUCT_TYPES
    with pytest.raises(ImproperlyConfigured):
        # invalid key format
        settings.SALESMAN_PRODUCT_TYPES = {"shop.Product.invalid": None}
        assert app_settings.SALESMAN_PRODUCT_TYPES
        del app_settings.SALESMAN_PRODUCT_TYPES
    # invalid product attrs
    settings.SALESMAN_PRODUCT_TYPES = {
        "shop.InvalidProduct": "shop.serializers.ProductSerializer",
    }
    with pytest.raises(ImproperlyConfigured):
        assert app_settings.SALESMAN_PRODUCT_TYPES
        del app_settings.SALESMAN_PRODUCT_TYPES
    # invalid product - no `get_price` method
    InvalidProduct.name = "Name"
    InvalidProduct.code = "Code"
    with pytest.raises(ImproperlyConfigured):
        assert app_settings.SALESMAN_PRODUCT_TYPES
        del app_settings.SALESMAN_PRODUCT_TYPES


class InvalidModifier:
    pass


class InvalidModifier2(BasketModifier):
    pass


class InvalidModifier3(BasketModifier):
    identifier = "id"


class InvalidModifier4(BasketModifier):
    identifier = "id"


def test_basket_modifiers(settings):
    assert isinstance(app_settings.SALESMAN_BASKET_MODIFIERS, list)
    del app_settings.SALESMAN_BASKET_MODIFIERS
    with pytest.raises(ImproperlyConfigured):
        # invalid path
        settings.SALESMAN_BASKET_MODIFIERS = ["invalid.Modifier"]
        assert app_settings.SALESMAN_BASKET_MODIFIERS
        del app_settings.SALESMAN_BASKET_MODIFIERS
    with pytest.raises(ImproperlyConfigured):
        # not extending class
        settings.SALESMAN_BASKET_MODIFIERS = ["tests.test_conf.InvalidModifier"]
        assert app_settings.SALESMAN_BASKET_MODIFIERS
        del app_settings.SALESMAN_BASKET_MODIFIERS
    with pytest.raises(ImproperlyConfigured):
        # missing identifier
        settings.SALESMAN_BASKET_MODIFIERS = ["tests.test_conf.InvalidModifier2"]
        assert app_settings.SALESMAN_BASKET_MODIFIERS
        del app_settings.SALESMAN_BASKET_MODIFIERS
    with pytest.raises(ImproperlyConfigured):
        # duplicate identifier
        settings.SALESMAN_BASKET_MODIFIERS = [
            "tests.test_conf.InvalidModifier3",
            "tests.test_conf.InvalidModifier4",
        ]
        assert app_settings.SALESMAN_BASKET_MODIFIERS
        del app_settings.SALESMAN_BASKET_MODIFIERS


not_callable_extra_validator_function = 1


def test_basket_extra_validator(settings):
    assert app_settings.SALESMAN_EXTRA_VALIDATOR
    del app_settings.SALESMAN_EXTRA_VALIDATOR
    with pytest.raises(ImproperlyConfigured):
        settings.SALESMAN_EXTRA_VALIDATOR = "invalid.path.to.function"
        assert app_settings.SALESMAN_EXTRA_VALIDATOR
        del app_settings.SALESMAN_EXTRA_VALIDATOR
    with pytest.raises(ImproperlyConfigured):
        settings.SALESMAN_EXTRA_VALIDATOR = (
            "tests.test_conf.not_callable_extra_validator_function"
        )
        assert app_settings.SALESMAN_EXTRA_VALIDATOR
        del app_settings.SALESMAN_EXTRA_VALIDATOR


class InvalidPayment:
    pass


class InvalidPayment2(PaymentMethod):
    pass


class InvalidPayment3(PaymentMethod):
    label = "label"


class InvalidPayment4(PaymentMethod):
    label = "label"
    identifier = "1"


class InvalidPayment5(PaymentMethod):
    label = "label"
    identifier = "1"


def test_payment_methods(settings):
    assert isinstance(app_settings.SALESMAN_PAYMENT_METHODS, list)
    del app_settings.SALESMAN_PAYMENT_METHODS
    with pytest.raises(ImproperlyConfigured):
        # invalid path
        settings.SALESMAN_PAYMENT_METHODS = ["invalid.Payment"]
        assert app_settings.SALESMAN_PAYMENT_METHODS
        del app_settings.SALESMAN_PAYMENT_METHODS
    with pytest.raises(ImproperlyConfigured):
        # not extending class
        settings.SALESMAN_PAYMENT_METHODS = ["tests.test_conf.InvalidPayment"]
        assert app_settings.SALESMAN_PAYMENT_METHODS
        del app_settings.SALESMAN_PAYMENT_METHODS
    with pytest.raises(ImproperlyConfigured):
        # missing label
        settings.SALESMAN_PAYMENT_METHODS = ["tests.test_conf.InvalidPayment2"]
        assert app_settings.SALESMAN_PAYMENT_METHODS
        del app_settings.SALESMAN_PAYMENT_METHODS
    with pytest.raises(ImproperlyConfigured):
        # missing identifier
        settings.SALESMAN_PAYMENT_METHODS = ["tests.test_conf.InvalidPayment3"]
        assert app_settings.SALESMAN_PAYMENT_METHODS
        del app_settings.SALESMAN_PAYMENT_METHODS
    with pytest.raises(ImproperlyConfigured):
        # duplicate identifier
        settings.SALESMAN_PAYMENT_METHODS = [
            "tests.test_conf.InvalidPayment4",
            "tests.test_conf.InvalidPayment5",
        ]
        assert app_settings.SALESMAN_PAYMENT_METHODS
        del app_settings.SALESMAN_PAYMENT_METHODS


not_callable_address_validator_function = 1


def test_address_validator(settings):
    assert app_settings.SALESMAN_ADDRESS_VALIDATOR
    del app_settings.SALESMAN_ADDRESS_VALIDATOR
    with pytest.raises(ImproperlyConfigured):
        settings.SALESMAN_ADDRESS_VALIDATOR = "invalid.path.to.function"
        assert app_settings.SALESMAN_ADDRESS_VALIDATOR
        del app_settings.SALESMAN_ADDRESS_VALIDATOR
    with pytest.raises(ImproperlyConfigured):
        settings.SALESMAN_ADDRESS_VALIDATOR = (
            "tests.test_conf.not_callable_address_validator_function"
        )
        assert app_settings.SALESMAN_ADDRESS_VALIDATOR
        del app_settings.SALESMAN_ADDRESS_VALIDATOR


class InvalidOrderStatusClass:
    pass


class InvalidOrderStatusClass2(BaseOrderStatus):
    NEW = "NEW"


def test_order_status(settings):
    assert app_settings.SALESMAN_ORDER_STATUS
    del app_settings.SALESMAN_ORDER_STATUS
    with pytest.raises(ImproperlyConfigured):
        settings.SALESMAN_ORDER_STATUS = "ivalid.path.to.class"
        assert app_settings.SALESMAN_ORDER_STATUS
        del app_settings.SALESMAN_ORDER_STATUS
    with pytest.raises(ImproperlyConfigured):
        settings.SALESMAN_ORDER_STATUS = "tests.test_conf.InvalidOrderStatusClass"
        assert app_settings.SALESMAN_ORDER_STATUS
        del app_settings.SALESMAN_ORDER_STATUS
    with pytest.raises(ImproperlyConfigured):
        settings.SALESMAN_ORDER_STATUS = "tests.test_conf.InvalidOrderStatusClass2"
        assert app_settings.SALESMAN_ORDER_STATUS
        del app_settings.SALESMAN_ORDER_STATUS


not_callable_reference_generator_function = 1


def test_order_reference_generator(settings):
    assert app_settings.SALESMAN_ORDER_REFERENCE_GENERATOR
    del app_settings.SALESMAN_ORDER_REFERENCE_GENERATOR
    with pytest.raises(ImproperlyConfigured):
        settings.SALESMAN_ORDER_REFERENCE_GENERATOR = "invalid.path.to.function"
        assert app_settings.SALESMAN_ORDER_REFERENCE_GENERATOR
        del app_settings.SALESMAN_ORDER_REFERENCE_GENERATOR
    with pytest.raises(ImproperlyConfigured):
        settings.SALESMAN_ORDER_REFERENCE_GENERATOR = (
            "tests.test_conf.not_callable_reference_generator_function"
        )
        assert app_settings.SALESMAN_ORDER_REFERENCE_GENERATOR
        del app_settings.SALESMAN_ORDER_REFERENCE_GENERATOR


def test_order_serializer(settings):
    assert app_settings.SALESMAN_ORDER_SERIALIZER
    del app_settings.SALESMAN_ORDER_SERIALIZER
    assert (
        app_settings.SALESMAN_ORDER_SUMMARY_SERIALIZER
        == app_settings.SALESMAN_ORDER_SERIALIZER
    )
    del app_settings.SALESMAN_ORDER_SUMMARY_SERIALIZER
    del app_settings.SALESMAN_ORDER_SERIALIZER

    with pytest.raises(ImproperlyConfigured):
        settings.SALESMAN_ORDER_SUMMARY_SERIALIZER = (
            "salesman.orders.serializers.DummyOrderSerializer"
        )
        assert app_settings.SALESMAN_ORDER_SUMMARY_SERIALIZER
        del app_settings.SALESMAN_ORDER_SUMMARY_SERIALIZER


not_callable_price_formatter_function = 1


def test_price_formatter(settings):
    assert app_settings.SALESMAN_PRICE_FORMATTER
    del app_settings.SALESMAN_PRICE_FORMATTER
    with pytest.raises(ImproperlyConfigured):
        settings.SALESMAN_PRICE_FORMATTER = "invalid.path.to.function"
        assert app_settings.SALESMAN_PRICE_FORMATTER
        del app_settings.SALESMAN_PRICE_FORMATTER
    with pytest.raises(ImproperlyConfigured):
        settings.SALESMAN_PRICE_FORMATTER = (
            "tests.test_conf.not_callable_price_formatter_function"
        )
        assert app_settings.SALESMAN_PRICE_FORMATTER
        del app_settings.SALESMAN_PRICE_FORMATTER


not_callable_admin_json_formatter_function = 1


def test_admin_json_formatter(settings):
    assert app_settings.SALESMAN_ADMIN_JSON_FORMATTER
    del app_settings.SALESMAN_ADMIN_JSON_FORMATTER
    with pytest.raises(ImproperlyConfigured):
        settings.SALESMAN_ADMIN_JSON_FORMATTER = "invalid.path.to.function"
        assert app_settings.SALESMAN_ADMIN_JSON_FORMATTER
        del app_settings.SALESMAN_ADMIN_JSON_FORMATTER
    with pytest.raises(ImproperlyConfigured):
        settings.SALESMAN_ADMIN_JSON_FORMATTER = (
            "tests.test_conf.not_callable_admin_json_formatter_function"
        )
        assert app_settings.SALESMAN_ADMIN_JSON_FORMATTER
        del app_settings.SALESMAN_ADMIN_JSON_FORMATTER
