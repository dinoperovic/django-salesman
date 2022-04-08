from __future__ import annotations

from typing import Any

from django.conf import settings
from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import URLPattern, URLResolver, path, reverse
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from salesman.conf import app_settings
from salesman.core.utils import get_salesman_model
from salesman.orders.models import BaseOrder, BaseOrderItem

from .utils import format_price


class BaseAdminMixin:
    """
    Mixin that adds formatters and display functions to the model admin.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        self.request = request
        return super().get_queryset(request)  # type: ignore


class OrderItemAdminMixin(BaseAdminMixin):
    """
    Admin mixin for Order Item model admin.
    """

    def product_data_display(self, obj: BaseOrderItem) -> str:
        return app_settings.SALESMAN_ADMIN_JSON_FORMATTER(
            obj.product_data, context={"order_item": True}
        )

    product_data_display.short_description = _("Product data")  # type: ignore

    def unit_price_display(self, obj: BaseOrderItem) -> str:
        return format_price(obj.unit_price, order=obj.order, request=self.request)

    unit_price_display.short_description = _("Unit price")  # type: ignore

    def subtotal_display(self, obj: BaseOrderItem) -> str:
        return format_price(obj.subtotal, order=obj.order, request=self.request)

    subtotal_display.short_description = _("Subtotal")  # type: ignore

    def total_display(self, obj: BaseOrderItem) -> str:
        return format_price(obj.total, order=obj.order, request=self.request)

    total_display.short_description = _("Total")  # type: ignore

    def extra_display(self, obj: BaseOrderItem) -> str:
        return app_settings.SALESMAN_ADMIN_JSON_FORMATTER(
            obj.extra, context={"order_item": True}
        )

    extra_display.short_description = _("Extra")  # type: ignore

    def extra_rows_display(self, obj: BaseOrderItem) -> str:
        return app_settings.SALESMAN_ADMIN_JSON_FORMATTER(
            obj.extra_rows, context={"order_item": True}
        )

    extra_rows_display.short_description = _("Extra rows")  # type: ignore


class OrderAdminMixin(BaseAdminMixin):
    """
    Admin mixin for Order model admin.
    """

    def extra_display(self, obj: BaseOrder) -> str:
        return app_settings.SALESMAN_ADMIN_JSON_FORMATTER(
            obj.extra, context={"order": True}
        )

    extra_display.short_description = _("Extra")  # type: ignore

    def extra_rows_display(self, obj: BaseOrder) -> str:
        return app_settings.SALESMAN_ADMIN_JSON_FORMATTER(
            obj.extra_rows, context={"order": True}
        )

    extra_rows_display.short_description = _("Extra rows")  # type: ignore

    def date_created_display(self, obj: BaseOrder) -> str:
        return date_format(obj.date_created, format="DATETIME_FORMAT")

    date_created_display.short_description = _("Date created")  # type: ignore

    def date_updated_display(self, obj: BaseOrder) -> str:
        return date_format(obj.date_updated, format="DATETIME_FORMAT")

    date_updated_display.short_description = _("Date updated")  # type: ignore

    def is_paid_display(self, obj: BaseOrder) -> bool:
        return obj.is_paid

    is_paid_display.boolean = True  # type: ignore
    is_paid_display.short_description = _("Is paid")  # type: ignore

    def customer_display(self, obj: BaseOrder) -> str:
        if not obj.user:
            return "-"
        app_label, model_name = settings.AUTH_USER_MODEL.lower().split(".")
        url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.user.id])
        return mark_safe(f'<a href="{url}">{obj.user}</a>')

    customer_display.short_description = _("Customer")  # type: ignore

    def shipping_address_display(self, obj: BaseOrder) -> str:
        return mark_safe(obj.shipping_address.replace("\n", "<br>")) or "-"

    shipping_address_display.short_description = _("Shipping address")  # type: ignore

    def billing_address_display(self, obj: BaseOrder) -> str:
        return mark_safe(obj.billing_address.replace("\n", "<br>")) or "-"

    billing_address_display.short_description = _("Billing address")  # type: ignore

    def subtotal_display(self, obj: BaseOrder) -> str:
        return format_price(obj.subtotal, order=obj, request=self.request)

    subtotal_display.short_description = _("Subtotal")  # type: ignore

    def total_display(self, obj: BaseOrder) -> str:
        return format_price(obj.total, order=obj, request=self.request)

    total_display.short_description = _("Total")  # type: ignore

    def amount_paid_display(self, obj: BaseOrder) -> str:
        return format_price(obj.amount_paid, order=obj, request=self.request)

    amount_paid_display.short_description = _("Amount paid")  # type: ignore

    def amount_outstanding_display(self, obj: BaseOrder) -> str:
        return format_price(obj.amount_outstanding, order=obj, request=self.request)

    amount_outstanding_display.short_description = _("Amount outstanding")  # type: ignore # noqa


class OrderAdminRefundMixin:
    """
    Mixin to add refund functionality to Order admin.
    """

    def get_urls(self) -> list[URLPattern | URLResolver]:
        urls: list[URLPattern | URLResolver] = super().get_urls()  # type: ignore
        urls += [
            path(
                "<path:object_id>/refund/",
                self.admin_site.admin_view(self.refund_view),  # type: ignore
                name="salesman_order_refund",
            ),
        ]
        return urls

    def refund_view(self, request: HttpRequest, object_id: int) -> HttpResponse:
        Order = get_salesman_model("Order")
        order = get_object_or_404(Order, id=object_id)

        app_label, model_name = app_settings.SALESMAN_ORDER_MODEL.lower().split(".")
        object_url = reverse(f"admin:{app_label}_{model_name}_change", args=[object_id])

        if "_refund-error" in request.POST:
            # Refund error, add error message and redirect to change view.
            msg = _("There was an error while trying to refund order.")
            self.message_user(  # type: ignore
                request, msg, messages.ERROR, fail_silently=True
            )
            return redirect(object_url)

        if "_refund-success" in request.POST:
            # Refund success, add success message and redirect to change view.
            failed = int(request.POST["_refund-success"])
            if failed:
                msg = _("The Order “{}” was only partially refunded.")
                status = messages.WARNING
            else:
                msg = _("The Order “{}” was successfully refunded.")
                status = messages.SUCCESS
            self.message_user(  # type: ignore
                request, msg.format(order), status, fail_silently=True
            )
            return redirect(object_url)

        context = {
            "title": _("Refund Order"),
            "object": order,
            "media": self.media,  # type: ignore
            "opts": self.model._meta,  # type: ignore
            "object_url": object_url,
        }
        return render(request, "salesman/admin/refund.html", context)
