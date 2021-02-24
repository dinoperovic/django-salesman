from django import forms
from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from salesman.conf import app_settings

from .models import Order, OrderItem, OrderNote, OrderPayment
from .widgets import OrderStatusSelect, PaymentSelect


class OrderItemInline(admin.TabularInline):
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

    def extra_rows_display(self, obj):
        template = '<div style="margin-top: -8px">{}</div>'
        return format_html(template, obj.extra_rows_display())

    extra_rows_display.short_description = _("Extra rows")

    def extra_display(self, obj):
        template = '<div style="margin-top: -8px">{}</div>'
        return format_html(template, obj.extra_display())

    extra_display.short_description = _("Extra")


class OrderPaymentModelForm(forms.ModelForm):
    class Meta:
        model = OrderPayment
        exclude = []
        widgets = {
            'payment_method': PaymentSelect,
        }


class OrderPaymentInline(admin.TabularInline):
    model = OrderPayment
    form = OrderPaymentModelForm
    fields = ['amount', 'transaction_id', 'payment_method', 'date_created']
    readonly_fields = ['date_created']
    extra = 0

    def get_queryset(self, request):
        self.model.request = request
        return super().get_queryset(request)


class OrderNoteModelForm(forms.ModelForm):
    class Meta:
        model = OrderNote
        exclude = []
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'cols': 60}),
        }


class OrderNoteInline(admin.TabularInline):
    model = OrderNote
    form = OrderNoteModelForm
    fields = ['message', 'public', 'date_created']
    readonly_fields = ['date_created']
    extra = 0


class OrderModelForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = []
        widgets = {
            'status': OrderStatusSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.order = self.instance

    def clean_status(self):
        status, order = self.cleaned_data['status'], self.instance
        return app_settings.SALESMAN_ORDER_STATUS.validate_transition(status, order)


class OrderStatusFilter(admin.SimpleListFilter):
    title = _('Status')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return app_settings.SALESMAN_ORDER_STATUS.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())


class OrderIsPaidFilter(admin.SimpleListFilter):
    title = _('Is paid')
    parameter_name = 'is_paid'

    def lookups(self, request, model_admin):
        return [('1', _('Yes')), ('0', _('No'))]

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(id__in=[x.id for x in queryset if x.is_paid])
        if self.value() == '0':
            return queryset.filter(id__in=[x.id for x in queryset if not x.is_paid])


class BaseOrderAdmin(admin.ModelAdmin):
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


class OrderRefundMixin(object):
    """
    Mixin to add refund functionality to Order admin.
    """

    def get_urls(self):
        urls = super().get_urls()
        return [
            path(
                '<path:object_id>/refund/',
                self.admin_site.admin_view(self.refund_view),
                name='salesman_order_refund',
            ),
        ] + urls

    def refund_view(self, request, object_id):
        order = get_object_or_404(Order, id=object_id)

        if '_refund-error' in request.POST:
            # Refund error, add error message and redirect to change view.
            msg = _("There was an error while trying to refund order.")
            self.message_user(request, msg, messages.ERROR, fail_silently=True)
            return redirect('admin:salesman_order_change', object_id)

        if '_refund-success' in request.POST:
            # Refund success, add success message and redirect to change view.
            failed = int(request.POST['_refund-success'])
            if failed:
                msg = _("The Order “{}” was only partially refunded.")
                status = messages.WARNING
            else:
                msg = _("The Order “{}” was successfully refunded.")
                status = messages.SUCCESS
            self.message_user(request, msg.format(order), status, fail_silently=True)
            return redirect('admin:salesman_order_change', object_id)

        context = {
            'title': _("Refund Order"),
            'object': order,
            'media': self.media,
            'opts': self.model._meta,
        }
        return render(request, 'salesman/admin/refund.html', context)


class OrderAdmin(OrderRefundMixin, BaseOrderAdmin):
    """
    Default Order admin with refund functionality.
    """


if app_settings.SALESMAN_ADMIN_REGISTER:
    admin.site.register(Order, OrderAdmin)
