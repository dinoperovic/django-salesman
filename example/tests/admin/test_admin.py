import pytest
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.urls import reverse

from salesman.admin import admin
from salesman.conf import app_settings
from salesman.core.utils import get_salesman_model
from shop.models import Product

site = AdminSite()

Order = get_salesman_model("Order")
OrderItem = get_salesman_model("OrderItem")
OrderPayment = get_salesman_model("OrderPayment")


@pytest.mark.django_db
def test_order_item_inline(rf, django_user_model):
    request = rf.get("/")
    request.user = django_user_model.objects.create_user(
        username="user", password="password"
    )
    modeladmin = admin.OrderItemInline(OrderItem, site)
    order = Order.objects.create(ref="1")
    product = Product.objects.create(name="Test", price=10)
    item = OrderItem.objects.create(
        order=order, product=product, unit_price=10, subtotal=20, total=20, quantity=2
    )
    modeladmin.get_queryset(request)
    assert modeladmin.model.request == request
    assert not modeladmin.has_add_permission(request, item)
    assert not modeladmin.has_delete_permission(request, item)


@pytest.mark.django_db
def test_order_payment_inline(rf, django_user_model):
    request = rf.get("/")
    request.user = django_user_model.objects.create_user(
        username="user", password="password"
    )
    modeladmin = admin.OrderPaymentInline(OrderPayment, site)
    order = Order.objects.create(ref="1")
    OrderPayment.objects.create(
        order=order, amount=100, transaction_id=1, payment_method="dummy"
    )
    modeladmin.get_queryset(request)
    assert modeladmin.model.request == request


@pytest.mark.django_db
def test_order_model_form():
    order = Order.objects.create(ref="1", subtotal=100, total=120)
    form = admin.OrderModelForm()
    form.cleaned_data = {"status": "COMPLETED"}
    form.instance = order
    with pytest.raises(ValidationError):
        assert form.clean_status()
    form.cleaned_data = {"status": "CREATED"}
    form.clean_status()


@pytest.mark.django_db
def test_order_admin(rf, django_user_model):
    request = rf.get("/")
    request.user = django_user_model.objects.create_user(
        username="user", password="password"
    )
    modeladmin = admin.OrderAdmin(Order, site)
    Order.objects.create(ref="0", subtotal=100, total=120)
    order = Order.objects.create(ref="1", subtotal=100, total=120)
    order2 = Order.objects.create(ref="2", subtotal=100, total=120)
    order2.pay(amount=120, transaction_id="1")
    assert len(modeladmin.get_queryset(request)) == 3
    assert modeladmin.model.request == request
    assert not modeladmin.has_add_permission(request, order)
    assert not modeladmin.has_delete_permission(request, order)

    # test refund view
    response = modeladmin.refund_view(request, order.id)
    assert response.status_code == 200
    request.POST = request.POST.dict()
    request.POST["_refund-error"] = "Error msg"
    response = modeladmin.refund_view(request, order.id)
    assert response.status_code == 302
    assert response.url == reverse("admin:shop_order_change", args=[order.id])
    del request.POST["_refund-error"]
    request.POST["_refund-success"] = "1"
    response = modeladmin.refund_view(request, order.id)
    assert response.status_code == 302
    request.POST["_refund-success"] = "0"
    response = modeladmin.refund_view(request, order.id)
    assert response.status_code == 302
    assert response.url == reverse("admin:shop_order_change", args=[order.id])

    # test status filter
    status_filter = admin.OrderStatusFilter(
        request, {"status": "NEW"}, order, modeladmin
    )
    assert (
        status_filter.lookups(request, modeladmin)
        == app_settings.SALESMAN_ORDER_STATUS.choices
    )
    assert status_filter.queryset(request, Order.objects.all()).count() == 3

    # test isPaid filter
    is_paid_filter = admin.OrderIsPaidFilter(
        request, {"is_paid": "1"}, order, modeladmin
    )
    assert is_paid_filter.lookups(request, modeladmin) == [("1", "Yes"), ("0", "No")]
    assert is_paid_filter.queryset(request, Order.objects.all()).count() == 1
    is_paid_filter = admin.OrderIsPaidFilter(
        request, {"is_paid": "0"}, order, modeladmin
    )
    assert is_paid_filter.queryset(request, Order.objects.all()).count() == 2
