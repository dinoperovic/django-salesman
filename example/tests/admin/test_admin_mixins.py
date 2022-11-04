from datetime import datetime

import pytest
from django.contrib.admin.sites import AdminSite
from django.urls import reverse
from django.utils.formats import date_format

from salesman.admin import admin
from salesman.admin.mixins import BaseAdminMixin, OrderAdminMixin, OrderItemAdminMixin
from salesman.admin.wagtail.mixins import WagtailOrderAdminMixin
from salesman.conf import app_settings
from salesman.core.utils import get_salesman_model
from shop.models import Product

site = AdminSite()

Order = get_salesman_model("Order")
OrderItem = get_salesman_model("OrderItem")


json_fmt = app_settings.SALESMAN_ADMIN_JSON_FORMATTER


def test_base_admin_mixin(rf):
    mixin_class = type("TestAdminMixin", (admin.OrderAdmin, BaseAdminMixin), {})
    mixin = mixin_class(Order, site, request=None)
    assert mixin.request is None
    request = rf.get("/")
    mixin.get_queryset(request)
    assert mixin.request == request


@pytest.mark.django_db
def test_order_item_admin_mixin():
    mixin = OrderItemAdminMixin()
    order = Order.objects.create(ref="1")
    extra = {"test": "123", "rows": ["value"]}
    product_data = {"name": "Test product"}
    product = Product.objects.create(name="Test Product", price=10)
    item = OrderItem.objects.create(
        order=order,
        product=product,
        unit_price=10,
        subtotal=20,
        total=20,
        quantity=2,
        _extra=extra,
        product_data=product_data,
    )

    assert mixin.product_data_display(item) == json_fmt(product_data)
    assert mixin.unit_price_display(item) == "10.00"
    assert mixin.subtotal_display(item) == "20.00"
    assert mixin.total_display(item) == "20.00"
    assert mixin.extra_display(item) == json_fmt(item.extra)
    assert mixin.extra_rows_display(item) == json_fmt(item.extra_rows)


@pytest.mark.django_db
def test_order_admin_mixin(django_user_model):
    user = django_user_model.objects.create_user(username="user", password="password")
    extra = {"test": "123", "rows": ["value"]}
    date = datetime.now()
    order = Order.objects.create(
        user=user,
        ref="1",
        subtotal=10,
        total=20,
        shipping_address="Test address shipping",
        billing_address="Test address billing",
        _extra=extra,
    )
    mixin = OrderAdminMixin()

    assert mixin.extra_display(order) == json_fmt(order.extra)
    assert mixin.extra_rows_display(order) == json_fmt(order.extra_rows)
    date_formated = date_format(date, format="DATETIME_FORMAT")
    assert mixin.date_created_display(order) == date_formated
    assert mixin.date_updated_display(order) == date_formated
    assert mixin.is_paid_display(order) is False
    url = reverse("admin:auth_user_change", args=[user.id])
    assert mixin.customer_display(order) == f'<a href="{url}">{user}</a>'
    order.user = None
    assert mixin.customer_display(order) == "-"
    assert mixin.shipping_address_display(order) == "Test address shipping"
    assert mixin.billing_address_display(order) == "Test address billing"
    assert mixin.subtotal_display(order) == "10.00"
    assert mixin.total_display(order) == "20.00"
    assert mixin.amount_paid_display(order) == "0.00"
    assert mixin.amount_outstanding_display(order) == "20.00"


@pytest.mark.django_db
def test_wagtail_order_admin_mixin(django_user_model):
    user = django_user_model.objects.create_user(username="user", password="password")
    order = Order.objects.create(user=user, status="COMPLETED")
    mixin = WagtailOrderAdminMixin()

    url = reverse("wagtailusers_users:edit", args=[user.id])
    assert mixin.customer_display(order) == f'<a href="{url}">{user}</a>'
    order.user = None
    assert mixin.customer_display(order) == "-"
    result = '<span class="status-tag primary">Completed</span>'
    assert mixin.status_display(order) == result
