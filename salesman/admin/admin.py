from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from salesman.conf import app_settings
from salesman.core.utils import get_salesman_model

from .filters import OrderIsPaidFilter, OrderStatusFilter
from .forms import OrderModelForm, OrderNoteModelForm, OrderPaymentModelForm
from .mixins import OrderAdminMixin, OrderAdminRefundMixin, OrderItemAdminMixin

Order = get_salesman_model('Order')
OrderItem = get_salesman_model('OrderItem')
OrderPayment = get_salesman_model('OrderPayment')
OrderNote = get_salesman_model('OrderNote')


class OrderItemInline(OrderItemAdminMixin, admin.TabularInline):
    model = OrderItem
    fields = [
        'name',
        'code',
        'unit_price_display',
        'quantity',
        'subtotal_display',
        'extra_rows_display',
        'total_display',
        'extra_display',
    ]
    readonly_fields = fields

    def get_queryset(self, request):
        self.model.request = request
        return super().get_queryset(request)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderPaymentInline(admin.TabularInline):
    model = OrderPayment
    form = OrderPaymentModelForm
    fields = ['amount', 'transaction_id', 'payment_method', 'date_created']
    readonly_fields = ['date_created']
    extra = 0

    def get_queryset(self, request):
        self.model.request = request
        return super().get_queryset(request)


class OrderNoteInline(admin.TabularInline):
    model = OrderNote
    form = OrderNoteModelForm
    fields = ['message', 'public', 'date_created']
    readonly_fields = ['date_created']
    extra = 0


class BaseOrderAdmin(OrderAdminMixin, admin.ModelAdmin):
    form = OrderModelForm
    change_form_template = 'salesman/admin/change_form.html'
    date_hierarchy = 'date_created'
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
    readonly_fields = [
        'user',
        'ref',
        'token',
        'status_display',
        'is_paid_display',
        'date_created',
        'date_updated',
        'customer_display',
        'email',
        'shipping_address_display',
        'billing_address_display',
        'subtotal_display',
        'total_display',
        'amount_paid_display',
        'amount_outstanding_display',
        'extra_display',
        'extra_rows_display',
    ]
    fieldsets = [
        (_("Info"), {'fields': ['ref', 'token']}),
        (
            _("Status"),
            {'fields': ['status', 'date_created', 'date_updated', 'is_paid_display']},
        ),
        (
            _("Contact"),
            {
                'fields': [
                    'customer_display',
                    'email',
                    'shipping_address_display',
                    'billing_address_display',
                ]
            },
        ),
        (
            _("Totals"),
            {
                'fields': [
                    'subtotal_display',
                    'extra_rows_display',
                    'total_display',
                    'amount_paid_display',
                    'amount_outstanding_display',
                ]
            },
        ),
        (_("Extra"), {'fields': ['extra_display']}),
    ]
    inlines = [OrderItemInline, OrderPaymentInline, OrderNoteInline]

    def get_queryset(self, request):
        self.model.request = request
        return super().get_queryset(request)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderAdmin(OrderAdminRefundMixin, BaseOrderAdmin):
    """
    Default Order admin with refund functionality.
    """


if app_settings.SALESMAN_ADMIN_REGISTER:
    admin.site.register(Order, OrderAdmin)
