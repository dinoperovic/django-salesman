import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from wagtail.admin.edit_handlers import EditHandler, FieldPanel, ObjectList

from salesman.admin import wagtail_hooks
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
    modeladmin.model = Order
    modeladmin.model.request = request
    edit_url = modeladmin.url_helper.get_action_url('edit', order.id)
    result = f'<span class="status-tag primary">{order.Status.NEW.label}</span>'
    assert modeladmin.status_display(order) == result
    order.status = order.Status.REFUNDED
    order.save()
    result = f'<span class="status-tag secondary">{order.Status.REFUNDED.label}</span>'
    assert modeladmin.status_display(order) == result

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

    # test get_edit_handler
    edit_handler = modeladmin.get_edit_handler(order, request)
    assert edit_handler == modeladmin.default_edit_handler
    modeladmin.default_edit_handler = None
    edit_handler = modeladmin.get_edit_handler(order, request)
    assert isinstance(edit_handler, ObjectList)
    modeladmin.model.panels = [FieldPanel('model_panel')]
    edit_handler = modeladmin.get_edit_handler(order, request)
    assert edit_handler.children == modeladmin.model.panels
    modeladmin.model.edit_handler = EditHandler(heading='model_edit_handler')
    edit_handler = modeladmin.get_edit_handler(order, request)
    assert edit_handler == modeladmin.model.edit_handler
    modeladmin.panels = [FieldPanel('admin_panel')]
    edit_handler = modeladmin.get_edit_handler(order, request)
    assert edit_handler.children == modeladmin.panels
    modeladmin.edit_handler = EditHandler(heading='admin_edit_handler')
    edit_handler = modeladmin.get_edit_handler(order, request)
    assert edit_handler == modeladmin.edit_handler
