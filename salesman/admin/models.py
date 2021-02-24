from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from salesman.conf import app_settings
from salesman.orders.models import Order as BaseOrder
from salesman.orders.models import OrderItem as BaseOrderItem
from salesman.orders.models import OrderNote as BaseOrderNote
from salesman.orders.models import OrderPayment as BaseOrderPayment

from .utils import format_price

__all__ = ['Order', 'OrderItem', 'OrderPayment', 'OrderNote']


class Order(BaseOrder):
    # Bound by modeladmin.
    request = None

    class Meta:
        proxy = True
        verbose_name = BaseOrder._meta.verbose_name
        verbose_name_plural = BaseOrder._meta.verbose_name_plural

    def extra_display(self):
        return app_settings.SALESMAN_ADMIN_JSON_FORMATTER(
            self.extra,
            context={'order': True},
        )

    extra_display.short_description = _("Extra")

    def extra_rows_display(self):
        return app_settings.SALESMAN_ADMIN_JSON_FORMATTER(
            self.extra_rows,
            context={'order': True},
        )

    extra_rows_display.short_description = _("Extra rows")

    def date_created_display(self):
        return date_format(self.date_created, format='DATETIME_FORMAT')

    date_created_display.short_description = _("Date created")

    def date_updated_display(self):
        return date_format(self.date_updated, format='DATETIME_FORMAT')

    date_updated_display.short_description = _("Date updated")

    def is_paid_display(self):
        return self.is_paid

    is_paid_display.boolean = True
    is_paid_display.short_description = _("Is paid")

    def customer_display(self, context={}):
        if not self.user:
            return '-'
        return app_settings.SALESMAN_ADMIN_CUSTOMER_FORMATTER(self.user, context)

    customer_display.short_description = _("Customer")

    def shipping_address_display(self):
        return mark_safe(self.shipping_address.replace('\n', '<br>')) or '-'

    shipping_address_display.short_description = _("Shipping address")

    def billing_address_display(self):
        return mark_safe(self.billing_address.replace('\n', '<br>')) or '-'

    billing_address_display.short_description = _("Billing address")

    def subtotal_display(self):
        return format_price(self.subtotal, order=self, request=self.request)

    subtotal_display.short_description = _("Subtotal")

    def total_display(self):
        return format_price(self.total, order=self, request=self.request)

    total_display.short_description = _("Total")

    def amount_paid_display(self):
        return format_price(self.amount_paid, order=self, request=self.request)

    amount_paid_display.short_description = _("Amount paid")

    def amount_outstanding_display(self):
        return format_price(self.amount_outstanding, order=self, request=self.request)

    amount_outstanding_display.short_description = _("Amount outstanding")


class OrderItem(BaseOrderItem):
    # Bound by modeladmin.
    request = None

    class Meta:
        proxy = True
        verbose_name = BaseOrderItem._meta.verbose_name
        verbose_name_plural = BaseOrderItem._meta.verbose_name_plural

    def product_data_display(self):
        return app_settings.SALESMAN_ADMIN_JSON_FORMATTER(
            self.product_data,
            context={'order_item': True},
        )

    product_data_display.short_description = _("Product data")

    def unit_price_display(self):
        return format_price(self.unit_price, order=self.order, request=self.request)

    unit_price_display.short_description = _("Unit price")

    def subtotal_display(self):
        return format_price(self.subtotal, order=self.order, request=self.request)

    subtotal_display.short_description = _("Subtotal")

    def total_display(self):
        return format_price(self.total, order=self.order, request=self.request)

    total_display.short_description = _("Total")

    def extra_display(self):
        return app_settings.SALESMAN_ADMIN_JSON_FORMATTER(
            self.extra,
            context={'order_item': True},
        )

    extra_display.short_description = _("Extra")

    def extra_rows_display(self):
        return app_settings.SALESMAN_ADMIN_JSON_FORMATTER(
            self.extra_rows,
            context={'order_item': True},
        )

    extra_rows_display.short_description = _("Extra rows")


class OrderPayment(BaseOrderPayment):
    # Bound by modeladmin.
    request = None

    class Meta:
        proxy = True
        verbose_name = BaseOrderPayment._meta.verbose_name
        verbose_name_plural = BaseOrderPayment._meta.verbose_name_plural

    def amount_display(self):
        return format_price(self.amount, order=self.order, request=self.request)

    amount_display.short_description = _("Amount")

    def date_created_display(self):
        return date_format(self.date_created, format='DATETIME_FORMAT')

    date_created_display.short_description = _("Date created")


class OrderNote(BaseOrderNote):
    class Meta:
        proxy = True
        verbose_name = BaseOrderNote._meta.verbose_name
        verbose_name_plural = BaseOrderNote._meta.verbose_name_plural
