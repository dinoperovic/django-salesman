from datetime import datetime
from decimal import Decimal

import pytest
from django.utils.formats import date_format

from salesman.admin import utils
from salesman.admin.edit_handlers import (
    OrderAdminPanel,
    OrderCheckboxPanel,
    OrderDatePanel,
    OrderItemsPanel,
    ReadOnlyPanel,
)
from salesman.admin.forms import WagtailOrderModelForm
from salesman.admin.mixins import OrderAdminMixin
from salesman.admin.wagtail_hooks import OrderAdmin
from salesman.core.utils import get_salesman_model

Order = get_salesman_model('Order')
OrderItem = get_salesman_model('OrderItem')


@pytest.mark.django_db
def test_read_only_panel():
    order = Order.objects.create(ref="1", subtotal=120, total=120)

    panel = ReadOnlyPanel('status')
    panel.model = Order
    panel.instance = order

    # test clone
    kwargs = panel.clone_kwargs()
    assert 'attr' in kwargs
    assert 'formatter' in kwargs
    assert 'renderer' in kwargs

    # test data from field set
    panel.on_model_bound()
    field = Order._meta.get_field('status')
    assert panel.heading == field.verbose_name
    assert panel.help_text == field.help_text

    # test render with formatter
    assert panel.render() == 'NEW'

    def _formatter(value, obj, request):
        return "<span>NEW</span>"

    panel.formatter = _formatter
    assert panel.render() == "<span>NEW</span>"

    # test render as with renderer
    assert panel.render_as_object().startswith('<fieldset><legend>Status</legend>')
    result = '<div class="field"><label>Status:</label>'
    assert panel.render_as_field().startswith(result)

    def _renderer(value, obj, request):
        return "<div>New</div>"

    panel.renderer = _renderer
    assert panel.render_as_object() == "<div>New</div>"
    assert panel.render_as_field() == "<div>New</div>"

    # test callable property
    panel = ReadOnlyPanel('total_display')
    panel.model = OrderAdminMixin
    panel.instance = OrderAdminMixin()
    panel.instance.total = Decimal('120')
    panel.on_model_bound()
    panel.on_form_bound()
    assert panel.heading == "Total"
    assert panel.render() == "120.00"
    panel.attr = "total_display_missing"
    panel.on_model_bound()
    assert panel.heading == "Total"


def test_order_date_panel():
    now = datetime.now()
    panel = OrderDatePanel('date')
    assert panel.format_value(now) == date_format(now, format='DATETIME_FORMAT')


def test_order_checkbox_panel():
    panel = OrderCheckboxPanel('bool')
    assert panel.format_value(True).startswith('<span class="icon icon-tick"')
    assert panel.format_value(False).startswith('<span class="icon icon-cross"')


@pytest.mark.django_db
def test_order_items_panel():
    order = Order.objects.create(ref="1", subtotal=120, total=120)
    OrderItem.objects.create(
        order=order, unit_price=50, subtotal=100, total=120, quantity=2
    )
    panel = OrderItemsPanel('items')
    panel.model = Order
    panel.instance = order

    assert panel.classes() == ['salesman-order-items']
    assert panel.render_as_field() == panel.render()
    assert panel.render_as_object() == panel.render()
    assert panel.format_json({'test': 1}, order, None) == utils.format_json({'test': 1})
    assert panel.render().startswith('<table class="listing full-width">')


@pytest.mark.django_db
def test_order_admin_panel():
    order = Order.objects.create(ref="1", subtotal=120, total=120)
    panel = OrderAdminPanel('total_display')
    panel.model = Order
    panel.instance = order
    panel.form = WagtailOrderModelForm()
    panel.on_model_bound()
    with pytest.raises(AssertionError):
        panel.on_form_bound()
    panel.form.model_admin = OrderAdmin()
    panel.on_form_bound()
    assert panel.heading == "Total"
    assert panel.get_value() == "120.00"
