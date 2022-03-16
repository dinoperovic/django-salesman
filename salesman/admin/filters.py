from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from salesman.conf import app_settings


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
