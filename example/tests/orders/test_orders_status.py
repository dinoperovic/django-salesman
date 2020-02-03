from salesman.orders.status import BaseOrderStatus


def test_base_order_status():
    assert BaseOrderStatus.get_payable() == []
    assert BaseOrderStatus.get_transitions() == {}
