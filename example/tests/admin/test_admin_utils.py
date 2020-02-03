from salesman.admin import utils


def test_format_json():
    data = {'test': 1}
    assert utils.format_json(data).startswith('<div><style>')
    assert utils.format_json(data, styled=False).startswith(
        '<div><pre style="margin: 0;">'
    )


def test_format_price():
    assert utils.format_price(1000, None, None) == '1000.00'
    assert utils.format_price(20, None, None) == '20.00'
    assert utils.format_price(-20, None, None) == '-20.00'
