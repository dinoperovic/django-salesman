from django import forms
from django.shortcuts import redirect
from django.urls import re_path
from django.utils.html import format_html
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
from salesman.core.utils import get_salesman_model

from .admin import OrderIsPaidFilter
from .admin import OrderModelForm as BaseOrderModelForm
from .admin import OrderStatusFilter
from .edit_handlers import (
    OrderAdminPanel,
    OrderCheckboxPanel,
    OrderCustomerPanel,
    OrderDatePanel,
    OrderItemsPanel,
    ReadOnlyPanel,
)
from .mixins import OrderAdminMixin
from .widgets import OrderStatusSelect, PaymentSelect

Order = get_salesman_model('Order')


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


class BaseOrderAdmin(OrderAdminMixin, ModelAdmin):
    model = Order
    menu_icon = 'form'
    index_view_class = OrderIndexView
    edit_view_class = OrderEditView
    list_display = [
        '__str__',
        'email',
        'admin_status',
        'total_display',
        'is_paid_display',
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
                    'status',
                    classname='choice_field',
                    widget=OrderStatusSelect,
                ),
                OrderDatePanel('date_created'),
                OrderDatePanel('date_updated'),
                OrderCheckboxPanel('is_paid', heading=_("Is paid")),
            ],
            heading=_("Status"),
        ),
        MultiFieldPanel(
            [
                OrderCustomerPanel('customer_display'),
                ReadOnlyPanel('email'),
                OrderAdminPanel('shipping_address_display'),
                OrderAdminPanel('billing_address_display'),
            ],
            heading=_("Contact"),
        ),
        MultiFieldPanel(
            [
                OrderAdminPanel('subtotal_display'),
                OrderAdminPanel('extra_rows_display'),
                OrderAdminPanel('total_display'),
                OrderAdminPanel('amount_paid_display'),
                OrderAdminPanel('amount_outstanding_display'),
            ],
            heading=_("Totals"),
        ),
        MultiFieldPanel([OrderAdminPanel('extra_display')], heading=_("Extra")),
    ]

    items_panels = [
        OrderItemsPanel('items', heading=_("Items")),
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
                OrderDatePanel('date_created'),
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
                OrderDatePanel('date_created'),
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

    def admin_status(self, obj):
        faded_statuses = [obj.statuses.CANCELLED, obj.statuses.REFUNDED]
        tag_class = 'secondary' if obj.status in faded_statuses else 'primary'
        template = '<span class="status-tag {}">{}</span>'
        return format_html(template, tag_class, obj.status_display)

    admin_status.short_description = _('Status')  # type: ignore

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
