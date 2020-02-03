import pytest
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.urls import reverse

from salesman.admin import admin, models
from salesman.conf import app_settings

site = AdminSite()


@pytest.mark.django_db
def test_order_item_inline(rf, django_user_model):
    request = rf.get('/')
    request.user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    modeladmin = admin.OrderItemInline(models.OrderItem, site)
    order = models.Order.objects.create(ref="1")
    item = models.OrderItem.objects.create(
        order=order, unit_price=10, subtotal=20, total=20, quantity=2
    )
    modeladmin.get_queryset(request)
    assert modeladmin.model.request == request
    assert not modeladmin.has_add_permission(request, item)
    assert not modeladmin.has_delete_permission(request, item)
    result = f'<div style="margin-top: -8px">{item.extra_rows_display()}</div>'
    assert modeladmin.extra_rows_display(item) == result
    result = f'<div style="margin-top: -8px">{item.extra_display()}</div>'
    assert modeladmin.extra_display(item) == result


@pytest.mark.django_db
def test_order_payment_inline(rf, django_user_model):
    request = rf.get('/')
    request.user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    modeladmin = admin.OrderPaymentInline(models.OrderPayment, site)
    order = models.Order.objects.create(ref="1")
    models.OrderPayment.objects.create(
        order=order, amount=100, transaction_id=1, payment_method='dummy'
    )
    modeladmin.get_queryset(request)
    assert modeladmin.model.request == request


@pytest.mark.django_db
def test_order_model_form():
    order = models.Order.objects.create(ref="1", subtotal=100, total=120)
    form = admin.OrderModelForm()
    form.cleaned_data = {'status': 'COMPLETED'}
    form.instance = order
    with pytest.raises(ValidationError):
        assert form.clean_status()
    form.cleaned_data = {'status': 'CREATED'}
    form.clean_status()


@pytest.mark.django_db
def test_order_admin(rf, django_user_model):
    request = rf.get('/')
    request.user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    modeladmin = admin.OrderAdmin(models.Order, site)
    models.Order.objects.create(ref="0", subtotal=100, total=120)
    order = models.Order.objects.create(ref="1", subtotal=100, total=120)
    order2 = models.Order.objects.create(ref="2", subtotal=100, total=120)
    order2.pay(amount=120, transaction_id='1')
    assert len(modeladmin.get_queryset(request)) == 3
    assert modeladmin.model.request == request
    assert not modeladmin.has_add_permission(request, order)
    assert not modeladmin.has_delete_permission(request, order)

    # test refund view
    response = modeladmin.refund_view(request, order.id)
    assert response.status_code == 200
    request.POST = request.POST.dict()
    request.POST['_refund-error'] = 'Error msg'
    response = modeladmin.refund_view(request, order.id)
    assert response.status_code == 302
    assert response.url == reverse('admin:salesman_order_change', args=[order.id])
    del request.POST['_refund-error']
    request.POST['_refund-success'] = '1'
    response = modeladmin.refund_view(request, order.id)
    assert response.status_code == 302
    request.POST['_refund-success'] = '0'
    response = modeladmin.refund_view(request, order.id)
    assert response.status_code == 302
    assert response.url == reverse('admin:salesman_order_change', args=[order.id])

    # test status filter
    status_filter = admin.OrderStatusFilter(
        request, {'status': 'NEW'}, order, modeladmin
    )
    assert (
        status_filter.lookups(request, modeladmin)
        == app_settings.SALESMAN_ORDER_STATUS.choices
    )
    assert status_filter.queryset(request, models.Order.objects.all()).count() == 3

    # test isPaid filter
    is_paid_filter = admin.OrderIsPaidFilter(
        request, {'is_paid': '1'}, order, modeladmin
    )
    assert is_paid_filter.lookups(request, modeladmin) == [('1', 'Yes'), ('0', 'No')]
    assert is_paid_filter.queryset(request, models.Order.objects.all()).count() == 1
    is_paid_filter = admin.OrderIsPaidFilter(
        request, {'is_paid': '0'}, order, modeladmin
    )
    assert is_paid_filter.queryset(request, models.Order.objects.all()).count() == 2
