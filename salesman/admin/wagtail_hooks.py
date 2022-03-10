from django import forms
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from salesman.conf import app_settings
from salesman.core.utils import get_salesman_model

from .edit_handlers import (
    OrderAdminPanel,
    OrderCheckboxPanel,
    OrderDatePanel,
    OrderItemsPanel,
    ReadOnlyPanel,
)
from .filters import OrderIsPaidFilter, OrderStatusFilter
from .forms import WagtailOrderModelForm
from .helpers import OrderButtonHelper, OrderPermissionHelper
from .mixins import WagtailOrderAdminMixin, WagtailOrderAdminRefundMixin
from .views import OrderEditView, OrderIndexView
from .widgets import OrderStatusSelect, PaymentSelect

Order = get_salesman_model('Order')


class BaseOrderAdmin(WagtailOrderAdminMixin, ModelAdmin):
    model = Order
    menu_icon = 'form'
    index_view_class = OrderIndexView
    edit_view_class = OrderEditView
    list_display = [
        '__str__',
        'email',
        'status_display',
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
                OrderAdminPanel('customer_display'),
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

    def get_edit_handler(self, instance, request):
        # Pass modeladmin to the form.
        admin_form_class = type(
            'WagtailOrderModelForm',
            (WagtailOrderModelForm,),
            {'model_admin': self},
        )
        return TabbedInterface(
            [
                ObjectList(self.panels, heading=_("Summary")),
                ObjectList(self.items_panels, heading=_("Items")),
                ObjectList(self.payments_panels, heading=_("Payments")),
                ObjectList(self.notes_panels, heading=_("Notes")),
            ],
            base_form_class=admin_form_class,
        )


class OrderAdmin(WagtailOrderAdminRefundMixin, BaseOrderAdmin):
    """
    Default Order admin with refund functionality.
    """


if app_settings.SALESMAN_ADMIN_REGISTER:
    modeladmin_register(OrderAdmin)
