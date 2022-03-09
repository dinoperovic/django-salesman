import pytest

from salesman.core.utils import get_salesman_model
from salesman.orders.signals import status_changed

Order = get_salesman_model('Order')

_signal_called = False


def on_status_changed(sender, order, new_status, old_status, **kwargs):
    global _signal_called
    _signal_called = True


@pytest.mark.django_db
def test_order_changed_signal(rf):
    status_changed.connect(on_status_changed, dispatch_uid="test_status_changed")
    order = Order.objects.create(ref="1", subtotal=100, total=100)
    order.status = order.statuses.COMPLETED
    order.save()
    assert _signal_called
    status_changed.disconnect(on_status_changed, dispatch_uid="test_status_changed")
