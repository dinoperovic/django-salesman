import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.utils.formats import date_format

from salesman.admin import utils, wagtail_hooks
from salesman.core.utils import get_salesman_model

site = AdminSite()

Order = get_salesman_model('Order')
OrderItem = get_salesman_model('OrderItem')


@pytest.mark.django_db
def test_order_admin(rf, client, django_user_model):
    request = rf.get('/')
    request.user = django_user_model.objects.create_superuser(
        username='user', password='password'
    )
    request.session = {}
    request._messages = FallbackStorage(request)
    order = Order.objects.create(ref="2020-00001", subtotal=100, total=120)
    OrderItem.objects.create(
        order=order, unit_price=10, subtotal=20, total=20, quantity=2
    )
    OrderItem.objects.create(order=order, unit_price=1, subtotal=2, total=2, quantity=1)
    modeladmin = wagtail_hooks.OrderAdmin()
    modeladmin.model.request = request
    edit_url = modeladmin.url_helper.get_action_url('edit', order.id)
    result = f'<span class="status-tag primary">{order.statuses.NEW.label}</span>'
    assert modeladmin.admin_status(order) == result
    order.status = order.statuses.REFUNDED
    order.save()
    result = (
        f'<span class="status-tag secondary">{order.statuses.REFUNDED.label}</span>'
    )
    assert modeladmin.admin_status(order) == result
    result = wagtail_hooks._format_is_paid(None, order, None)
    assert modeladmin.admin_is_paid(order) == result

    # test _formatters.
    result = utils.format_json({'test': 1})
    assert wagtail_hooks._format_json({'test': 1}, None, None) == result
    result = '<span class="icon icon-cross" style="color: #cd3238;"></span>'
    assert wagtail_hooks._format_is_paid(None, order, None) == result
    result = date_format(order.date_created, format='DATETIME_FORMAT')
    assert wagtail_hooks._format_date(order.date_created, order, request) == result

    # test _renderers.
    result = wagtail_hooks._render_items(None, order, request)
    assert result.startswith('<table class="listing full-width">')
    assert result.count('<tr>') == 3

    # test index/edit view
    edit_view = modeladmin.edit_view_class(modeladmin, str(order.id))
    assert edit_view.get_success_url() == edit_url
    assert edit_view.get_meta_title() == 'Viewing Order'
    client.login(username='user', password='password')
    client.get(edit_url)
    response = client.get(modeladmin.url_helper.get_action_url('index'))
    assert modeladmin.model.request == response._request

    # test permission helper
    assert not modeladmin.permission_helper.user_can_create(request.user)
    assert not modeladmin.permission_helper.user_can_delete_obj(request.user, order)

    # test button helper
    helper = modeladmin.button_helper_class(edit_view, request)
    assert helper.edit_button(order.id)['label'] == 'View'
    assert helper.edit_button(order.id)['title'] == 'View this Order'

    # test refund
    response = modeladmin.refund_view(request, str(order.id))
    assert response.status_code == 200
    view = modeladmin.refund_view_class(modeladmin, str(order.id))
    request.POST = request.POST.dict()
    request.POST['_refund-error'] = 'Error msg'
    response = view.post(request, str(order.id))
    assert response.status_code == 302
    assert response.url == edit_url
    del request.POST['_refund-error']
    request.POST['_refund-success'] = '1'
    response = view.post(request, str(order.id))
    assert response.status_code == 302
    request.POST['_refund-success'] = '0'
    response = view.post(request, str(order.id))
    assert response.status_code == 302
    assert response.url == edit_url
    assert view.get_meta_title() == 'Confirm Order refund'
