from __future__ import annotations

import copy
from decimal import Decimal
from secrets import token_urlsafe
from typing import Any, Optional, Type

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.http import HttpRequest
from django.utils.functional import cached_property, classproperty
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _

from salesman.basket.models import BaseBasket, BaseBasketItem
from salesman.conf import app_settings
from salesman.core.typing import Product
from salesman.core.utils import get_salesman_model
from salesman.orders.status import BaseOrderStatus

from .signals import status_changed

try:
    # Add support for Wagtail admin.
    from modelcluster.fields import ParentalKey
    from modelcluster.models import ClusterableModel
except ImportError:  # pragma: no cover
    ClusterableModel = models.Model
    ParentalKey = models.ForeignKey


class ParentalForeignKey(ParentalKey):
    """
    Use this foreign key to add support for Wagtail
    in case modelcluster is installed.
    """


class OrderManager(models.Manager):
    def create_from_request(self, request: HttpRequest, **kwargs) -> BaseOrder:
        """
        Create new order with reference. Items are still in basket and should
        be added using ``order.populate_from_basket(basket, request)`` method.

        Returns:
            Order: Order instance
        """
        kwargs['ref'] = app_settings.SALESMAN_ORDER_REFERENCE_GENERATOR(request)
        return super().create(**kwargs)

    def create_from_basket(
        self,
        basket: BaseBasket,
        request: HttpRequest,
        **kwargs,
    ) -> BaseOrder:
        """
        Create and populate new order from basket.

        Returns:
            Order: Order instance
        """
        kwargs['ref'] = app_settings.SALESMAN_ORDER_REFERENCE_GENERATOR(request)
        order = self.model(**kwargs)
        order.populate_from_basket(basket, request)
        return order


class BaseOrder(ClusterableModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("User"),
    )

    # A unique reference to this order, could be used as order number.
    ref = models.CharField(
        _("Reference"),
        max_length=128,
        unique=True,
        help_text=_("A unique order reference."),
    )

    # Current order status.
    status = models.CharField(
        _("Status"),
        max_length=128,
        default='NEW',
        help_text=_("Changing order status might trigger a notification to customer."),
    )

    # A unique token to allow non-authenticated user access to order.
    token = models.CharField(
        _("Token"),
        max_length=128,
        unique=True,
        default=token_urlsafe,
        help_text=_(
            "Allow non-authenticated customer to access the order with token. "
            "To access order suply a '?token={token}' in url querystring."
        ),
    )

    # Customer contact info.
    email = models.EmailField(_("Email"), blank=True)
    shipping_address = models.TextField(_("Shipping address"), blank=True)
    billing_address = models.TextField(_("Billing address"), blank=True)

    subtotal = models.DecimalField(
        _("Subtotal"), max_digits=18, decimal_places=2, default=Decimal(0)
    )
    total = models.DecimalField(
        _("Total"), max_digits=18, decimal_places=2, default=Decimal(0)
    )
    _extra = models.JSONField(_("Extra"), blank=True, default=dict)

    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date updated"), auto_now=True)

    objects = OrderManager()

    # Separate rows from `_extra` to `extra_rows`.
    extra: Optional[dict] = None
    extra_rows: Optional[list] = None

    _current_status = None
    _cached_items: Optional[list[BaseOrderItem]] = None

    class Meta:
        abstract = True
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ['-date_created']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra = copy.deepcopy(self._extra)
        self.extra_rows = self.extra.pop('rows', [])
        self._current_status = self.status

    def __str__(self):
        return self.ref

    def save(self, *args, **kwargs):
        self._extra = dict(self.extra, rows=self.extra_rows)
        if 'extra' in kwargs.get('update_fields', []):
            kwargs['update_fields'].remove('extra')
            kwargs['update_fields'].append('_extra')
        new_status, old_status = self.status, self._current_status
        super().save(*args, **kwargs)
        # Send signal if status changed.
        if new_status != old_status:
            status_changed.send(
                get_salesman_model('Order'),
                order=self,
                new_status=new_status,
                old_status=old_status,
            )

    def pay(
        self,
        amount: Decimal,
        transaction_id: str,
        payment_method: str = '',
    ) -> BaseOrderPayment:
        """
        Create a new payment for order.

        Args:
            amount (Decimal): Amount to add
            transaction_id (str): ID of transaction
            payment_method (str, optional): Payment method identifier. Defaults to ''.

        Returns:
            OrderPayment: New order payment instance
        """
        OrderPayment = get_salesman_model('OrderPayment')
        return OrderPayment.objects.create(
            order=self,
            amount=amount,
            transaction_id=transaction_id,
            payment_method=payment_method,
        )

    @transaction.atomic
    def populate_from_basket(
        self,
        basket: BaseBasket,
        request: HttpRequest,
        **kwargs,
    ) -> None:
        """
        Populate order with items from basket.

        Args:
            basket (Basket): Basket instance
            request (HttpRequest): Django request
        """
        from salesman.basket.serializers import ExtraRowsField

        if not hasattr(basket, 'total'):
            basket.update(request)

        self.user = basket.user
        self.email = basket.extra.pop('email', '')
        self.shipping_address = basket.extra.pop('shipping_address', '')
        self.billing_address = basket.extra.pop('billing_address', '')
        self.subtotal = basket.subtotal
        self.total = basket.total
        self.extra = basket.extra
        self.extra_rows = ExtraRowsField().to_representation(basket.extra_rows)
        if self.status == self.Status.NEW:
            self.status = self.Status.CREATED
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.save()

        OrderItem = get_salesman_model('OrderItem')
        for item in basket.get_items():
            obj = OrderItem(order=self)
            obj.populate_from_basket_item(item, request)
            obj.save()

    def get_items(self) -> list[BaseOrderItem]:
        """
        Returns items from cache or stores new ones.
        """
        if self._cached_items is None:
            self._cached_items = list(self.items.all())
        return self._cached_items

    @classproperty
    def Status(cls) -> Type[BaseOrderStatus]:
        """
        Return order status enum from settings.
        """
        return app_settings.SALESMAN_ORDER_STATUS

    @property
    def status_display(self) -> str:
        """
        Returns display label for current status.
        """
        return str(dict(self.Status.choices).get(self.status, self.status))

    status_display.fget.short_description = _("Status")  # type: ignore
    status_display.fget.admin_order_field = 'status'  # type: ignore

    @cached_property
    def amount_paid(self) -> Decimal:
        """
        Returns amount already paid for this order.
        """
        return Decimal(sum([x.amount for x in self.payments.all()]))

    @property
    def amount_outstanding(self) -> Decimal:
        """
        Returns amount still needed for order to be paid.
        """
        return Decimal(self.total - self.amount_paid)

    @property
    def is_paid(self) -> bool:
        """
        Returns if order is paid in full.
        """
        return self.amount_paid >= self.total

    @classmethod
    def get_wagtail_admin_attribute(cls, name: str) -> Optional[Any]:
        """
        Return attribute from Wagtail order admin mixin.

        Args:
            name (str): Attribute name

        Returns:
            Optional[Any]: Attribute value
        """
        if (
            'salesman.admin' in settings.INSTALLED_APPS
            and 'wagtail.admin' in settings.INSTALLED_APPS
            and 'wagtail.contrib.modeladmin' in settings.INSTALLED_APPS
        ):
            from salesman.admin.wagtail.mixins import WagtailOrderAdminMixin

            return getattr(WagtailOrderAdminMixin, name, None)
        return None

    @classproperty
    def default_panels(cls) -> Optional[list]:
        return cls.get_wagtail_admin_attribute("default_panels")

    @classproperty
    def default_items_panels(cls) -> Optional[list]:
        return cls.get_wagtail_admin_attribute("default_items_panels")

    @classproperty
    def default_payments_panels(cls) -> Optional[list]:
        return cls.get_wagtail_admin_attribute("default_payments_panels")

    @classproperty
    def default_notes_panels(cls) -> Optional[list]:
        return cls.get_wagtail_admin_attribute("default_notes_panels")

    @classproperty
    def default_edit_handler(cls) -> Optional[Any]:
        return cls.get_wagtail_admin_attribute("default_edit_handler")


class Order(BaseOrder):
    """
    Model that can be swapped by overriding `SALESMAN_ORDER_MODEL` setting.
    """

    class Meta(BaseOrder.Meta):
        swappable = 'SALESMAN_ORDER_MODEL'


class BaseOrderItem(models.Model):
    order = ParentalForeignKey(
        app_settings.SALESMAN_ORDER_MODEL,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_("Order"),
    )

    product_type = models.CharField(_("Product type"), max_length=128)

    # Generic relation to product (optional).
    product_content_type = models.ForeignKey(ContentType, models.SET_NULL, null=True)
    product_id = models.PositiveIntegerField(_("Product id"), null=True)
    product: Product = GenericForeignKey('product_content_type', 'product_id')

    # Stored product serializer data at the moment of purchase.
    product_data = models.JSONField(_("Product data"), blank=True, default=dict)

    unit_price = models.DecimalField(_("Unit price"), max_digits=18, decimal_places=2)
    subtotal = models.DecimalField(_("Subtotal"), max_digits=18, decimal_places=2)
    total = models.DecimalField(_("Total"), max_digits=18, decimal_places=2)
    quantity = models.PositiveIntegerField(_("Quantity"))
    _extra = models.JSONField(_("Extra"), blank=True, default=dict)

    # Separate rows from `_extra` to `extra_rows`.
    extra: Optional[dict] = None
    extra_rows: Optional[list] = None

    class Meta:
        abstract = True
        verbose_name = _("Item")
        verbose_name_plural = _("Items")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra = copy.deepcopy(self._extra)
        self.extra_rows = self.extra.pop('rows', [])

    def __str__(self):
        return f'{self.quantity}x {self.name} ({self.code})'

    def save(self, *args, **kwargs):
        self._extra = dict(self.extra, rows=self.extra_rows)
        if 'extra' in kwargs.get('update_fields', []):
            kwargs['update_fields'].remove('extra')
            kwargs['update_fields'].append('_extra')
        super().save(*args, **kwargs)

    def populate_from_basket_item(
        self,
        item: BaseBasketItem,
        request: HttpRequest,
    ) -> None:
        """
        Populate order with items from basket.

        Args:
            item (BasketItem): Basket item instance
            request (HttpRequest): Django request
        """
        from salesman.basket.serializers import ExtraRowsField, ProductField

        self.product_type = item.product._meta.label
        self.product_content_type = item.product_content_type
        self.product_id = item.product_id

        # Store serialized product with `name` and `code`.
        product_field = ProductField()
        product_field._context = {"request": request}
        product_data = product_field.to_representation(item.product)
        product_data.update({'name': item.product.name, 'code': item.product.code})
        self.product_data = product_data

        self.unit_price = item.unit_price
        self.subtotal = item.subtotal
        self.total = item.total
        self.quantity = item.quantity
        self.extra = item.extra
        self.extra_rows = ExtraRowsField().to_representation(item.extra_rows)

    @property
    def name(self):
        """
        Returns product `name` from stored data.
        """
        return self.product_data.get('name', "(no name)")

    @property
    def code(self):
        """
        Returns product `name` from stored data.
        """
        return self.product_data.get('code', "(no code)")


class OrderItem(BaseOrderItem):
    """
    Model that can be swapped by overriding `SALESMAN_ORDER_ITEM_MODEL` setting.
    """

    class Meta(BaseOrderItem.Meta):
        swappable = 'SALESMAN_ORDER_ITEM_MODEL'


class BaseOrderPayment(models.Model):
    order = ParentalForeignKey(
        app_settings.SALESMAN_ORDER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_("Order"),
    )

    amount = models.DecimalField(_("Amount"), max_digits=18, decimal_places=2)
    transaction_id = models.CharField(_("Transaction ID"), max_length=128)
    payment_method = models.CharField(_("Payment method"), max_length=128, blank=True)

    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)

    class Meta:
        abstract = True
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        unique_together = ('order', 'transaction_id')

    def __str__(self):
        return f'{self.amount} ({self.transaction_id})'

    def get_payment_method(self):
        """
        Returns payment method instance.
        """
        from salesman.checkout.payment import payment_methods_pool

        return payment_methods_pool.get_payment(self.payment_method)

    @property
    def payment_method_display(self):
        """
        Returns display label for payment method.
        """
        payment = self.get_payment_method()
        return payment.label if payment else self.payment_method

    payment_method_display.fget.short_description = _("Payment method")  # type: ignore


class OrderPayment(BaseOrderPayment):
    """
    Model that can be swapped by overriding `SALESMAN_ORDER_PAYMENT_MODEL` setting.
    """

    class Meta(BaseOrderPayment.Meta):
        swappable = 'SALESMAN_ORDER_PAYMENT_MODEL'


class BaseOrderNote(models.Model):
    order = ParentalForeignKey(
        app_settings.SALESMAN_ORDER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_("Order"),
    )

    message = models.TextField(_("Message"))
    public = models.BooleanField(
        _("Public"), default=False, help_text=_("Is accessible to the customer?")
    )

    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)

    class Meta:
        abstract = True
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")

    def __str__(self):
        return Truncator(self.message).words(3)


class OrderNote(BaseOrderNote):
    """
    Model that can be swapped by overriding `SALESMAN_ORDER_NOTE_MODEL` setting.
    """

    class Meta(BaseOrderNote.Meta):
        swappable = 'SALESMAN_ORDER_NOTE_MODEL'
