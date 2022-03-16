from __future__ import annotations

from collections import OrderedDict
from decimal import Decimal
from typing import Optional, Tuple

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.http import HttpRequest
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from salesman.conf import app_settings
from salesman.core.utils import get_salesman_model

BASKET_ID_SESSION_KEY = 'BASKET_ID'


class BasketManager(models.Manager):
    def get_or_create_from_request(
        self,
        request: HttpRequest,
    ) -> Tuple[BaseBasket, bool]:
        """
        Get basket from request or create a new one.
        If user is logged in session basket gets merged into a user basket.

        Returns:
            tuple: (basket, created)
        """
        if not hasattr(request, 'session'):
            request.session = {}
        try:
            session_basket_id = request.session[BASKET_ID_SESSION_KEY]
            session_basket = self.get(id=session_basket_id, owner=None)
        except (KeyError, self.model.DoesNotExist):
            session_basket = None

        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                basket, created = self.get_or_create(owner_id=request.user.id)
            except self.model.MultipleObjectsReturned:
                # User has multiple baskets, merge them.
                baskets = list(self.filter(owner=request.user.id))
                basket, created = baskets[0], False
                for other in baskets[1:]:
                    basket.merge(other)

            if session_basket:
                # Merge session basket into user basket.
                basket.merge(session_basket)

            if BASKET_ID_SESSION_KEY in request.session:
                # Delete session basket id from session so that it doesn't get
                # re-fetched while user is still logged in.
                del request.session[BASKET_ID_SESSION_KEY]
        else:
            basket, created = session_basket or self.create(), not session_basket
            request.session[BASKET_ID_SESSION_KEY] = basket.id

        return basket, created


class BaseBasket(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_("Owner"),
    )

    extra = models.JSONField(_("Extra"), blank=True, default=dict)

    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date updated"), auto_now=True)

    objects = BasketManager()

    _cached_items: Optional[list[BaseBasketItem]] = None

    class Meta:
        abstract = True
        verbose_name = _("Basket")
        verbose_name_plural = _("Baskets")
        ordering = ['-date_created']

    def __str__(self):
        return str(self.pk) if self.pk else "(unsaved)"

    def __iter__(self):
        for item in self.items.all():
            yield item

    def update(self, request: HttpRequest) -> None:
        """
        Process basket with modifiers defined in ``SALESMAN_BASKET_MODIFIERS``.
        This method sets ``subtotal``, ``total`` and ``extra_rows`` attributes on the
        basket and updates the items. Should be called every time the basket item is
        added, removed or updated or basket extra is updated.

        Args:
            request (HttpRequest): Django request
        """
        from .modifiers import basket_modifiers_pool

        items = self.get_items()

        # Setup basket and items.
        for modifier in basket_modifiers_pool.get_modifiers():
            modifier.setup_basket(self, request)
            for item in items:
                modifier.setup_item(item, request)

        self.extra_rows: dict = OrderedDict()
        self.subtotal = Decimal(0)
        self.total = Decimal(0)

        # Process basket items.
        for item in items:
            item.update(request)
            self.subtotal += item.total
        self.total = self.subtotal

        # Finalize items and process basket.
        for modifier in basket_modifiers_pool.get_modifiers():
            for item in items:
                modifier.finalize_item(item, request)
            modifier.process_basket(self, request)

        # Finalize basket.
        for modifier in basket_modifiers_pool.get_modifiers():
            modifier.finalize_basket(self, request)

        self._cached_items = items

    def add(
        self,
        product: object,
        quantity: int = 1,
        ref: Optional[str] = None,
        extra: Optional[dict] = None,
    ) -> BaseBasketItem:
        """
        Add product to the basket.

        Returns:
            BasketItem: BasketItem instance
        """
        BasketItem = get_salesman_model('BasketItem')
        if not ref:
            ref = BasketItem.get_product_ref(product)
        try:
            item = self.items.get(ref=ref)
            item.quantity += quantity
            item.extra = extra or item.extra
            item.save(update_fields=['quantity', 'extra', 'date_updated'])
        except BasketItem.DoesNotExist:
            item = BasketItem.objects.create(
                basket=self,
                product=product,
                quantity=quantity,
                ref=ref,
                extra=extra or {},
            )
        self._cached_items = None
        return item

    def remove(self, ref: str) -> None:
        """
        Remove item with given ``ref`` from the basket.

        Args:
            ref (str): Item ref to remove
        """
        item = self.find(ref)
        if item:
            item.delete()
            self._cached_items = None

    def find(self, ref: str) -> Optional[BaseBasketItem]:
        """
        Find item with given ``ref`` in the basket.

        Args:
            ref (str): Item ref

        Returns:
            Optional[BaseBasketItem]: Basket item if found.
        """
        if self._cached_items is not None:
            try:
                return [item for item in self._cached_items if item.ref == ref][0]
            except IndexError:
                return None
        return self.items.filter(ref=ref).first()

    def clear(self) -> None:
        """
        Clear all items from the basket.
        """
        self.items.all().delete()
        self._cached_items = None

    @transaction.atomic
    def merge(self, other: BaseBasket) -> None:
        """
        Merge other basket with this one, delete afterwards.

        Args:
            other (Basket): Basket which to merge
        """
        for item in other:
            try:
                existing = self.items.get(ref=item.ref)
                existing.quantity += item.quantity
                existing.save(update_fields=['quantity'])
            except item.DoesNotExist:
                item.basket = self
                item.save(update_fields=['basket'])
        other.delete()
        self._cached_items = None

    def get_items(self) -> list[BaseBasketItem]:
        """
        Returns items from cache or stores new ones.
        """
        if self._cached_items is None:
            self._cached_items = list(self.items.all().prefetch_related('product'))
        return self._cached_items

    @property
    def count(self) -> int:
        """
        Returns basket item count.
        """
        if self._cached_items is not None:
            return len(self._cached_items)
        return self.items.count()

    @property
    def quantity(self) -> int:
        """
        Returns the total quantity of all items in a basket.
        """
        if self._cached_items is not None:
            return sum([item.quantity for item in self._cached_items])
        aggr = self.items.aggregate(quantity=models.Sum('quantity'))
        return aggr['quantity'] or 0


class Basket(BaseBasket):
    """
    Model that can be swapped by overriding `SALESMAN_BASKET_MODEL` setting.
    """

    class Meta(BaseBasket.Meta):
        swappable = 'SALESMAN_BASKET_MODEL'


class BaseBasketItem(models.Model):
    basket = models.ForeignKey(
        app_settings.SALESMAN_BASKET_MODEL,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_("Basket"),
    )

    # Reference to this basket item, used to determine item duplicates.
    ref = models.SlugField(_("Reference"), max_length=128)

    # Generic relation to product.
    product_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    product_id = models.PositiveIntegerField(_("Product id"))
    product = GenericForeignKey('product_content_type', 'product_id')

    quantity = models.PositiveIntegerField(_("Quantity"), default=1)
    extra = models.JSONField(_("Extra"), blank=True, default=dict)

    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date updated"), auto_now=True)

    class Meta:
        abstract = True
        verbose_name = _("Item")
        verbose_name_plural = _("Items")
        unique_together = ('basket', 'ref')
        ordering = ['date_created']

    def __str__(self):
        return f'{self.quantity}x {self.product}'

    def save(self, *args, **kwargs):
        # Set default ref.
        if not self.ref:
            self.ref = self.get_product_ref(self.product)
        super().save(*args, **kwargs)

    def update(self, request: HttpRequest) -> None:
        """
        Process items with modifiers defined in ``SALESMAN_BASKET_MODIFIERS``.
        This method sets ``unit_price``, ``subtotal``, ``total`` and ``extra_rows``
        attributes on the item. Should be called every time the basket item
        is added, removed or updated.

        Args:
            request (HttpRequest): Django request
        """
        from .modifiers import basket_modifiers_pool

        self.extra_rows: dict = OrderedDict()
        self.unit_price = Decimal(self.product.get_price(request))
        self.subtotal = self.unit_price * self.quantity
        self.total = self.subtotal

        for modifier in basket_modifiers_pool.get_modifiers():
            modifier.process_item(self, request)

    @property
    def name(self):
        """
        Returns product `name`.
        """
        return self.product.name

    @property
    def code(self):
        """
        Returns product `name`.
        """
        return self.product.code

    @classmethod
    def get_product_ref(cls, product: models.Model) -> str:
        """
        Returns default item ``ref`` for given product.

        Args:
            product (models.Model): Product instance

        Returns:
            str: Item ref
        """
        return slugify(f'{product._meta.label}-{product.id}')


class BasketItem(BaseBasketItem):
    """
    Model that can be swapped by overriding `SALESMAN_BASKET_ITEM_MODEL` setting.
    """

    class Meta(BaseBasketItem.Meta):
        swappable = 'SALESMAN_BASKET_ITEM_MODEL'
