import pytest

from salesman.checkout.payment import PaymentMethod, payment_methods_pool


def test_base_payment_method():
    method = PaymentMethod()
    assert method.get_urls() == []
    with pytest.raises(NotImplementedError):
        method.basket_payment(None, None)
    with pytest.raises(NotImplementedError):
        method.order_payment(None, None)
    assert not method.refund_payment(None)


def test_payment_methods_pool():
    assert len(payment_methods_pool.get_payments()) == 3
    assert len(payment_methods_pool.get_payments("order")) == 2
    assert len(payment_methods_pool.get_payments("basket")) == 1
    assert len(payment_methods_pool.get_urls()) == 3
    assert len(payment_methods_pool.get_choices()) == 3
    assert len(payment_methods_pool.get_choices("order")) == 2
    assert len(payment_methods_pool.get_choices("basket")) == 1
    assert payment_methods_pool.get_payment("dummy2").label == "Dummy 2"
    assert not payment_methods_pool.get_payment("non-existant")
