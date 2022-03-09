from decimal import Decimal

import pytest

from salesman.core import utils
from shop.models.basket import Basket, BasketItem
from shop.models.order import Order, OrderItem, OrderNote, OrderPayment


def test_format_price():
    assert utils.format_price(10) == '10.00'
    assert utils.format_price(1.5) == '1.50'
    assert utils.format_price(1000) == '1000.00'
    assert utils.format_price(Decimal(13.3)) == '13.30'


def test_get_salesman_model():
    assert utils.get_salesman_model('Basket') == Basket
    assert utils.get_salesman_model('BasketItem') == BasketItem
    assert utils.get_salesman_model('Order') == Order
    assert utils.get_salesman_model('OrderItem') == OrderItem
    assert utils.get_salesman_model('OrderPayment') == OrderPayment
    assert utils.get_salesman_model('OrderNote') == OrderNote

    with pytest.raises(ValueError):
        assert utils.get_salesman_model('NonValidModel')
