from typing import Type

from django.db.models import Model
from django.http import HttpRequest
from wagtail.admin.edit_handlers import EditHandler, ObjectList
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from salesman.conf import app_settings
from salesman.core.utils import get_salesman_model

from .filters import OrderIsPaidFilter, OrderStatusFilter
from .forms import WagtailOrderModelForm
from .helpers import OrderAdminURLHelper, OrderButtonHelper, OrderPermissionHelper
from .mixins import WagtailOrderAdminMixin, WagtailOrderAdminRefundMixin
from .views import OrderEditView, OrderIndexView

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
    url_helper_class = OrderAdminURLHelper
    form_view_extra_css = ['salesman/admin/wagtail_form.css']

    def get_base_form_class(self) -> Type[WagtailOrderModelForm]:
        """
        Returns Model form class with model_admin instance attached.

        Returns:
            type[WagtailOrderModelForm]: A model form class
        """
        return type(
            'WagtailOrderModelForm',
            (WagtailOrderModelForm,),
            {'model_admin': self},
        )

    def get_edit_handler(self, instance: Model, request: HttpRequest) -> EditHandler:
        """
        Returns edit handler with custom base form class attached.

        Args:
            instance (Model): Model instance
            request (HttpRequest): Django request

        Returns:
            EditHandler: Edit handler
        """
        if hasattr(self, 'edit_handler'):
            edit_handler = self.edit_handler
        elif hasattr(self, 'panels'):
            panels = self.panels
            edit_handler = ObjectList(panels)
        elif hasattr(self.model, 'edit_handler'):
            edit_handler = self.model.edit_handler
        elif hasattr(self.model, 'panels'):
            panels = self.model.panels
            edit_handler = ObjectList(panels)
        elif hasattr(self, 'default_edit_handler') and self.default_edit_handler:
            edit_handler = self.default_edit_handler
        else:
            edit_handler = super().get_edit_handler(instance, request)

        edit_handler.base_form_class = self.get_base_form_class()
        return edit_handler


class OrderAdmin(WagtailOrderAdminRefundMixin, BaseOrderAdmin):
    """
    Default Order admin with refund functionality.
    """


if app_settings.SALESMAN_ADMIN_REGISTER:
    modeladmin_register(OrderAdmin)
