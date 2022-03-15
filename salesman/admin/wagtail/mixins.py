from django import forms
from django.urls import re_path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)

from ..mixins import OrderAdminMixin
from ..widgets import OrderStatusSelect, PaymentSelect
from .edit_handlers import (
    OrderAdminPanel,
    OrderCheckboxPanel,
    OrderDatePanel,
    OrderItemsPanel,
    ReadOnlyPanel,
)
from .views import OrderRefundView


class WagtailOrderAdminMixin(OrderAdminMixin):
    """
    Wagtail Order admin mixin.
    Panel definitions are here to avoid circular dependencies when importing.
    """

    default_panels = [
        MultiFieldPanel(
            [
                ReadOnlyPanel('ref'),
                ReadOnlyPanel('token'),
            ],
            heading=_("Info"),
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

    default_items_panels = [
        OrderItemsPanel('items', heading=_("Items")),
    ]

    default_payments_panels = [
        InlinePanel(
            'payments',
            [
                FieldPanel('amount'),
                FieldPanel('transaction_id'),
                FieldPanel(
                    'payment_method',
                    classname='choice_field',
                    widget=PaymentSelect,
                ),
                OrderDatePanel('date_created'),
            ],
            heading=_("Payments"),
        ),
    ]

    default_notes_panels = [
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

    default_edit_handler = TabbedInterface(
        [
            ObjectList(default_panels, heading=_("Summary")),
            ObjectList(default_items_panels, heading=_("Items")),
            ObjectList(default_payments_panels, heading=_("Payments")),
            ObjectList(default_notes_panels, heading=_("Notes")),
        ]
    )

    def customer_display(self, obj):
        if not obj.user:
            return '-'
        url = reverse('wagtailusers_users:edit', args=[obj.user.id])
        return mark_safe(f'<a href="{url}">{obj.user}</a>')

    customer_display.short_description = _("Customer")  # type: ignore

    def status_display(self, obj):
        faded_statuses = [obj.Status.CANCELLED, obj.Status.REFUNDED]
        tag_class = 'secondary' if obj.status in faded_statuses else 'primary'
        template = '<span class="status-tag {}">{}</span>'
        return format_html(template, tag_class, obj.status_display)

    status_display.short_description = _('Status')  # type: ignore


class WagtailOrderAdminRefundMixin:
    """
    Mixin to add refund functionality to Wagtail Order admin.
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
