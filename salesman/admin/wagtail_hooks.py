from django import forms
from django.shortcuts import redirect
from django.urls import re_path
from django.utils.formats import date_format
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from wagtail.admin import messages
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.admin.forms import WagtailAdminModelForm
from wagtail.contrib.modeladmin.helpers import ButtonHelper, PermissionHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.contrib.modeladmin.views import DeleteView, EditView, IndexView

from salesman.conf import app_settings

from .admin import OrderIsPaidFilter
from .admin import OrderModelForm as BaseOrderModelForm
from .admin import OrderStatusFilter
from .edit_handlers import ReadOnlyPanel
from .models import Order
from .utils import format_price
from .widgets import OrderStatusSelect, PaymentSelect


def _format_json(value, obj, request):
    """
    Wrapper for ``format_json`` temporarily used to display
    json values on inline order models.
    """
    return app_settings.SALESMAN_ADMIN_JSON_FORMATTER(
        value,
        context={'order_item': True},
    )


def _format_date(value, obj, request):
    """
    Wrapper for ``date_format`` used to display date values
    on inline order models.
    """
    return date_format(value, format='DATETIME_FORMAT')


def _format_is_paid(value, obj, request):
    """
    Formatter for is_paid to display colored tick or cross.
    """
    icon, color = ('tick', '#157b57') if obj.is_paid else ('cross', '#cd3238')
    template = '<span class="icon icon-{}" style="color: {};"></span>'
    return format_html(template, icon, color)


def _format_customer(value, obj, request):
    """
    Wrapper for displaying customer in Wagtail.
    """
    return obj.customer_display(context={'wagtail': True})


def _render_items(value, obj, request):
    """
    Renderer to display items table statically in html format.
    """
    head = f'''<tr>
        <td>{_('Name')}</td>
        <td>{_('Code')}</td>
        <td>{_('Unit price')}</td>
        <td>{_('Quantity')}</td>
        <td>{_('Subtotal')}</td>
        <td>{_('Extra rows')}</td>
        <td>{_('Total')}</td>
        <td>{_('Extra')}</td>
        </tr>'''

    body = ''
    for item in obj.items.all():
        body += '<tr>'
        body += f'<td class="title"><h2>{item.name}</h2></td>'
        body += f'<td>{item.code}</td>'
        body += f'<td>{format_price(item.unit_price, obj, request)}</td>'
        body += f'<td>{item.quantity}</td>'
        body += f'<td>{format_price(item.subtotal, obj, request)}</td>'
        body += f'<td>{_format_json(item.extra_rows, obj, request)}</td>'
        body += f'<td>{format_price(item.total, obj, request)}</td>'
        body += f'<td>{_format_json(item.extra, obj, request)}</td>'
        body += '</tr>'

    return format_html(
        '<table class="listing full-width">'
        '<thead>{}</thead>'
        '<tbody>{}</tbody>'
        '</table>',
        mark_safe(head),
        mark_safe(body),
    )


class OrderIndexView(IndexView):
    """
    Wagtail admin view that handles Order index.
    """

    def dispatch(self, request, *args, **kwargs):
        self.model.request = request
        return super().dispatch(request, *args, **kwargs)


class OrderEditView(EditView):
    """
    Wagtail admin view that handles Order edit.
    """

    page_title = _('Order')

    def dispatch(self, request, *args, **kwargs):
        self.model.request = request
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.edit_url

    def get_meta_title(self):
        return _('Viewing Order')


class OrderPermissionHelper(PermissionHelper):
    def user_can_create(self, user):
        return False

    def user_can_delete_obj(self, user, obj):
        return False


class OrderButtonHelper(ButtonHelper):
    def edit_button(self, *args, **kwargs):
        button = super().edit_button(*args, **kwargs)
        button.update({'label': _("View"), 'title': _("View this Order")})
        return button


class OrderModelForm(BaseOrderModelForm, WagtailAdminModelForm):
    pass


class BaseOrderAdmin(ModelAdmin):
    model = Order
    menu_icon = 'form'
    index_view_class = OrderIndexView
    edit_view_class = OrderEditView
    list_display = [
        'admin_title',
        'email',
        'admin_status',
        'total_display',
        'admin_is_paid',
        'date_created',
    ]
    list_filter = [OrderStatusFilter, OrderIsPaidFilter, 'date_created', 'date_updated']
    search_fields = ['ref', 'email', 'token']
    edit_template_name = 'salesman/admin/wagtail_edit.html'
    permission_helper_class = OrderPermissionHelper
    button_helper_class = OrderButtonHelper
    form_view_extra_css = ['salesman/admin/wagtail_form.css']

    panels = [
        MultiFieldPanel(
            [ReadOnlyPanel('ref'), ReadOnlyPanel('token')], heading=_("Info")
        ),
        MultiFieldPanel(
            [
                FieldPanel(
                    'status', classname='choice_field', widget=OrderStatusSelect
                ),
                ReadOnlyPanel('date_created_display'),
                ReadOnlyPanel('date_updated_display'),
                ReadOnlyPanel('is_paid_display', formatter=_format_is_paid),
            ],
            heading=_("Status"),
        ),
        MultiFieldPanel(
            [
                ReadOnlyPanel('customer_display', formatter=_format_customer),
                ReadOnlyPanel('email'),
                ReadOnlyPanel('shipping_address_display'),
                ReadOnlyPanel('billing_address_display'),
            ],
            heading=_("Contact"),
        ),
        MultiFieldPanel(
            [
                ReadOnlyPanel('subtotal_display'),
                ReadOnlyPanel('extra_rows_display'),
                ReadOnlyPanel('total_display'),
                ReadOnlyPanel('amount_paid_display'),
                ReadOnlyPanel('amount_outstanding_display'),
            ],
            heading=_("Totals"),
        ),
        MultiFieldPanel([ReadOnlyPanel('extra_display')], heading=_("Extra")),
    ]

    # Currently proxy related models don't work in Django and can't be used when
    # accessing them on an Order proxy through a related manager. It points back to
    # original models for items and payments. For that reason we can't use "display"
    # methods defined on proxy related models and are using formatter/renderer
    # functions instead.

    items_panels = [
        ReadOnlyPanel(
            'items',
            classname='salesman-order-items',
            renderer=_render_items,
            heading=_("Items"),
        ),
    ]

    payments_panels = [
        InlinePanel(
            'payments',
            [
                FieldPanel('amount'),
                FieldPanel('transaction_id'),
                FieldPanel(
                    'payment_method', classname='choice_field', widget=PaymentSelect
                ),
                ReadOnlyPanel('date_created', formatter=_format_date),
            ],
            heading=_("Payments"),
        ),
    ]

    notes_panels = [
        InlinePanel(
            'notes',
            [
                FieldPanel('message', widget=forms.Textarea(attrs={'rows': 4})),
                FieldPanel('public'),
                ReadOnlyPanel('date_created', formatter=_format_date),
            ],
            heading=_("Notes"),
        )
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(panels, heading=_("Summary")),
            ObjectList(items_panels, heading=_("Items")),
            ObjectList(payments_panels, heading=_("Payments")),
            ObjectList(notes_panels, heading=_("Notes")),
        ],
        base_form_class=OrderModelForm,
    )

    def admin_title(self, obj):
        url = self.url_helper.get_action_url('edit', obj.id)
        return format_html(
            '<div class="title">'
            '<div class="title-wrapper"><a href="{}">{}</a></div>'
            '</div>',
            url,
            obj,
        )

    admin_title.short_description = _('Order')

    def admin_status(self, obj):
        faded_statuses = [obj.statuses.CANCELLED, obj.statuses.REFUNDED]
        tag_class = 'secondary' if obj.status in faded_statuses else 'primary'
        template = '<span class="status-tag {}">{}</span>'
        return format_html(template, tag_class, obj.status_display)

    admin_status.short_description = _('Status')

    def admin_is_paid(self, obj):
        return _format_is_paid(None, obj, None)

    admin_is_paid.short_description = Order.is_paid_display.short_description

    def get_edit_template(self):
        return super().get_edit_template()


class OrderRefundView(DeleteView):
    """
    Wagtail admin view that handles Order refunds.
    """

    page_title = _('Refund')

    def check_action_permitted(self, user):
        return True

    def get_meta_title(self):
        return _('Confirm Order refund')

    def post(self, request, *args, **kwargs):
        if '_refund-error' in request.POST:
            # Refund error, add error message and redirect to change view.
            msg = _("There was an error while trying to refund order.")
            messages.error(request, msg)

        if '_refund-success' in request.POST:
            # Refund success, add success message and redirect to change view.
            failed = int(request.POST['_refund-success'])
            if failed:
                msg = _("The Order “{}” was only partially refunded.")
                messages.warning(request, msg.format(self.instance))
            else:
                msg = _("The Order “{}” was successfully refunded.")
                messages.success(request, msg.format(self.instance))

        return redirect(self.edit_url)

    def get_template_names(self):
        return ['salesman/admin/wagtail_refund.html']


class OrderRefundMixin(object):
    """
    Mixin to add refund functionality to Order admin.
    """

    refund_view_class = OrderRefundView

    def get_admin_urls_for_registration(self):
        urls = super().get_admin_urls_for_registration()
        urls += (
            re_path(
                self.url_helper.get_action_url_pattern('refund'),
                self.refund_view,
                name=self.url_helper.get_action_url_name('refund'),
            ),
        )
        return urls

    def refund_view(self, request, instance_pk):
        kwargs = {'model_admin': self, 'instance_pk': instance_pk}
        view_class = self.refund_view_class
        return view_class.as_view(**kwargs)(request)


class OrderAdmin(OrderRefundMixin, BaseOrderAdmin):
    """
    Default Order admin with refund functionality.
    """


if app_settings.SALESMAN_ADMIN_REGISTER:
    modeladmin_register(OrderAdmin)
