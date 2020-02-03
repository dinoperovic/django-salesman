from decimal import Decimal

from salesman.core import utils


def test_format_price():
    assert utils.format_price(10) == '10.00'
    assert utils.format_price(1.5) == '1.50'
    assert utils.format_price(1000) == '1000.00'
    assert utils.format_price(Decimal(13.3)) == '13.30'
