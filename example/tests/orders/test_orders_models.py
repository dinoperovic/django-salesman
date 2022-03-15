from decimal import Decimal

import pytest

from salesman.admin.mixins import WagtailOrderAdminMixin
from salesman.conf import app_settings
from salesman.core.utils import get_salesman_model
from shop.models import Product

Basket = get_salesman_model('Basket')
Order = get_salesman_model('Order')
OrderItem = get_salesman_model('OrderItem')
OrderPayment = get_salesman_model('OrderPayment')
OrderNote = get_salesman_model('OrderNote')


@pytest.mark.django_db
def test_create_from_request(rf):
    request = rf.get('/')
    order_ref = app_settings.SALESMAN_ORDER_REFERENCE_GENERATOR(request)
    order = Order.objects.create_from_request(request)
    assert str(order) == order_ref


@pytest.mark.django_db
def test_create_and_populate_from_basket(rf):
    request = rf.get('/')
    product = Product.objects.create(name="Test", price=100)
    product2 = Product.objects.create(name="Test #2", price=30)
    basket, _ = Basket.objects.get_or_create_from_request(request)
    basket.add(product)
    basket.add(product2)
    basket.update(request)
    assert basket.count == 2
    total = basket.total
    subtotal = basket.subtotal
    extra_rows = basket.extra_rows
    delattr(basket, 'total')  # delete to trigger update in `populate_from_basket`
    order = Order.objects.create_from_basket(basket, request)
    assert order.items.count() == 2
    assert order.total == total
    assert order.subtotal == subtotal
    assert order.extra == basket.extra
    assert len(order.extra_rows) == len(extra_rows)
    # Test populate with kwargs
    order2 = Order.objects.create_from_request(request)
    order2.populate_from_basket(basket, request, status=order2.Status.COMPLETED)
    assert order2.status == order2.Status.COMPLETED


@pytest.mark.django_db
def test_order_properties(rf, settings):
    order = Order.objects.create(
        ref="1",
        email="user@example.com",
        subtotal=70,
        total=80,
        _extra={'test': 1, 'rows': [1, 2]},
    )  # noqa
    order.pay(amount=50, transaction_id=1, payment_method='dummy')
    assert order.payments.count() == 1
    # extra, extra_rows
    assert order.extra == {'test': 1}
    assert order.extra_rows == [1, 2]
    order.extra['x'] = 'x'
    order.extra.update({'test': 2})
    order.save(update_fields=['extra'])
    assert order.extra == {'test': 2, 'x': 'x'}
    # amounts, is_paid
    assert order.amount_paid == Decimal(50)
    assert order.amount_outstanding == Decimal(30)
    assert not order.is_paid
    OrderPayment.objects.create(
        order=order, amount=30, transaction_id=2, payment_method='dummy'
    )
    del order.amount_paid  # delete property since it's cached
    assert order.amount_outstanding == 0
    assert order.is_paid
    # status
    order.status = order.Status.COMPLETED
    order.save(update_fields=['status'])
    assert order.status_display == 'Completed'
    # wagtail attributes
    assert order.default_panels == WagtailOrderAdminMixin.default_panels
    assert order.default_items_panels == WagtailOrderAdminMixin.default_items_panels
    assert (
        order.default_payments_panels == WagtailOrderAdminMixin.default_payments_panels
    )
    assert order.default_notes_panels == WagtailOrderAdminMixin.default_notes_panels
    assert order.default_edit_handler == WagtailOrderAdminMixin.default_edit_handler
    settings.INSTALLED_APPS.remove('salesman.admin')
    assert order.get_wagtail_admin_attribute('default_edit_hanlder') is None


@pytest.mark.django_db
def test_order_item_properties(rf):
    product = Product.objects.create(name="Test", price=100)
    order = Order.objects.create(ref="1")
    item = OrderItem.objects.create(
        order=order,
        product=product,
        unit_price=100,
        subtotal=100,
        total=100,
        quantity=1,
        product_data={'name': "Test data", 'code': '1'},
    )
    assert str(item) == "1x Test data (1)"  # product_data['name']
    item.product.delete()
    assert str(item) == "1x Test data (1)"  # product_data['name']
    assert item.code == "1"
    del item.product_data['name']
    del item.product_data['code']
    item.save()
    assert str(item) == "1x (no name) ((no code))"  # empty product_data
    assert item.code == "(no code)"
    # extra
    item.extra['test'] = 1
    item.save(update_fields=['extra'])
    assert 'test' in item.extra


@pytest.mark.django_db
def test_order_payment():
    # test str
    payment = OrderPayment(amount=100, transaction_id="test_id", payment_method='dummy')
    assert str(payment) == "100 (test_id)"
    # test getters
    assert payment.get_payment_method().identifier == 'dummy'
    assert payment.payment_method_display == 'Dummy'


def test_order_note():
    # test str
    note1 = OrderNote(message="This is a test message")
    note2 = OrderNote(message="Some-thing basic")
    assert str(note1) == "This is a…"
    assert str(note2) == "Some-thing basic"
