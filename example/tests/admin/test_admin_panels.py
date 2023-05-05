from datetime import datetime
from decimal import Decimal

import pytest
from django.utils.formats import date_format
from wagtail.utils.version import get_main_version as get_wagtail_version

from salesman.admin import utils
from salesman.admin.mixins import OrderAdminMixin
from salesman.admin.wagtail.forms import WagtailOrderModelForm
from salesman.admin.wagtail.panels import (
    OrderAdminPanel,
    OrderCheckboxPanel,
    OrderDatePanel,
    OrderItemsPanel,
    ReadOnlyPanel,
)
from salesman.admin.wagtail_hooks import OrderAdmin
from salesman.core.utils import get_salesman_model
from shop.models import Product

Order = get_salesman_model("Order")
OrderItem = get_salesman_model("OrderItem")

WAGTAIL_VERSION = get_wagtail_version()


@pytest.mark.django_db
def test_read_only_panel():
    order = Order.objects.create(ref="1", subtotal=120, total=120)

    panel = ReadOnlyPanel("status")
    panel.model = Order

    # test clone
    kwargs = panel.clone_kwargs()
    assert "attr" in kwargs
    assert "formatter" in kwargs
    assert "renderer" in kwargs

    # test data from field set
    panel.on_model_bound()
    field = Order._meta.get_field("status")
    assert panel.heading == field.verbose_name
    assert panel.help_text == field.help_text

    if WAGTAIL_VERSION >= "4.0.0":
        bound_panel = panel.BoundPanel(
            panel, instance=order, request=None, form=None, prefix=None
        )
    elif WAGTAIL_VERSION >= "3.0.0":
        bound_panel = panel.BoundPanel(panel, instance=order, request=None, form=None)
    else:
        bound_panel = panel
        bound_panel.instance = order

    # test render with formatter
    assert bound_panel.render() == "NEW"

    def _formatter(value, obj, request):
        return "<span>NEW</span>"

    bound_panel.formatter = _formatter
    assert bound_panel.render() == "<span>NEW</span>"

    # test render as with renderer
    assert bound_panel.render_as_object().startswith(
        "<fieldset><legend>Status</legend>"
    )
    result = '<div class="field"><label>Status:</label>'
    assert bound_panel.render_as_field().startswith(result)

    def _renderer(value, obj, request):
        return "<div>New</div>"

    bound_panel.renderer = _renderer
    assert bound_panel.render_as_object() == "<div>New</div>"
    assert bound_panel.render_as_field() == "<div>New</div>"

    # test callable property
    panel = ReadOnlyPanel("total_display")
    panel.model = OrderAdminMixin
    instance = OrderAdminMixin()
    instance.total = Decimal("120")

    if WAGTAIL_VERSION >= "4.0.0":
        bound_panel = panel.BoundPanel(
            panel, instance=instance, request=None, form=None, prefix=None
        )
    elif WAGTAIL_VERSION >= "3.0.0":
        bound_panel = panel.BoundPanel(
            panel, instance=instance, request=None, form=None
        )
    else:
        bound_panel = panel
        bound_panel.instance = instance

    panel.on_model_bound()
    assert panel.heading == "Total"
    assert bound_panel.render() == "120.00"
    panel.attr = "total_display_missing"
    panel.on_model_bound()
    assert panel.heading == "Total"


def test_order_date_panel():
    now = datetime.now()
    panel = OrderDatePanel("date")
    assert panel.format_value(now) == date_format(now, format="DATETIME_FORMAT")


def test_order_checkbox_panel():
    panel = OrderCheckboxPanel("bool")
    assert panel.format_value(True).startswith('<span class="icon icon-tick"')
    assert panel.format_value(False).startswith('<span class="icon icon-cross"')


@pytest.mark.django_db
def test_order_items_panel():
    order = Order.objects.create(ref="1", subtotal=120, total=120)
    product = Product.objects.create(name="Test Product", price=50)
    OrderItem.objects.create(
        order=order, product=product, unit_price=50, subtotal=100, total=120, quantity=2
    )
    panel = OrderItemsPanel("items")
    panel.model = Order

    if WAGTAIL_VERSION >= "4.0.0":
        bound_panel = panel.BoundPanel(
            panel, instance=order, request=None, form=None, prefix=None
        )
    elif WAGTAIL_VERSION >= "3.0.0":
        bound_panel = panel.BoundPanel(panel, instance=order, request=None, form=None)
    else:
        bound_panel = panel
        bound_panel.instance = order

    assert bound_panel.classes() == ["salesman-order-items"]
    assert bound_panel.render_as_field() == bound_panel.render()
    assert bound_panel.render_as_object() == bound_panel.render()
    assert bound_panel.format_json({"test": 1}, order, None) == utils.format_json(
        {"test": 1}
    )
    assert bound_panel.render().startswith('<table class="listing full-width">')


@pytest.mark.django_db
def test_order_admin_panel():
    order = Order.objects.create(ref="1", subtotal=120, total=120)
    panel = OrderAdminPanel("total_display")
    panel.model = Order

    if WAGTAIL_VERSION >= "4.0.0":
        form = WagtailOrderModelForm()
        with pytest.raises(AssertionError):
            bound_panel = panel.BoundPanel(
                panel, instance=order, request=None, form=form, prefix=None
            )
        form.model_admin = OrderAdmin()
        bound_panel = panel.BoundPanel(
            panel, instance=order, request=None, form=form, prefix=None
        )
    elif WAGTAIL_VERSION >= "3.0.0":
        form = WagtailOrderModelForm()
        with pytest.raises(AssertionError):
            bound_panel = panel.BoundPanel(
                panel, instance=order, request=None, form=form
            )
        form.model_admin = OrderAdmin()
        bound_panel = panel.BoundPanel(panel, instance=order, request=None, form=form)
    else:
        bound_panel = panel
        bound_panel.instance = order
        bound_panel.form = WagtailOrderModelForm()
        bound_panel.form.model_admin = OrderAdmin()
        bound_panel.on_form_bound()

    panel.on_model_bound()
    assert bound_panel.heading == "Total"
    assert bound_panel.get_value() == "120.00"
