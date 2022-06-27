from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from salesman.conf import app_settings
from salesman.orders.models import BaseOrder

if TYPE_CHECKING:  # pragma: no cover
    from .admin import BaseOrderAdmin


class OrderStatusFilter(admin.SimpleListFilter):
    title = _("Status")
    parameter_name = "status"

    def lookups(
        self,
        request: HttpRequest,
        model_admin: BaseOrderAdmin,
    ) -> list[tuple[str, str]]:
        return app_settings.SALESMAN_ORDER_STATUS.choices

    def queryset(
        self,
        request: HttpRequest,
        queryset: QuerySet[BaseOrder],
    ) -> QuerySet[BaseOrder] | None:
        if self.value():
            return queryset.filter(status=self.value())
        return None


class OrderIsPaidFilter(admin.SimpleListFilter):
    title = _("Is paid")
    parameter_name = "is_paid"

    def lookups(
        self,
        request: HttpRequest,
        model_admin: BaseOrderAdmin,
    ) -> list[tuple[str, str]]:
        return [("1", _("Yes")), ("0", _("No"))]

    def queryset(
        self,
        request: HttpRequest,
        queryset: QuerySet[BaseOrder],
    ) -> QuerySet[BaseOrder] | None:
        if self.value() == "1":
            return queryset.filter(id__in=[x.id for x in queryset if x.is_paid])
        if self.value() == "0":
            return queryset.filter(id__in=[x.id for x in queryset if not x.is_paid])
        return None
