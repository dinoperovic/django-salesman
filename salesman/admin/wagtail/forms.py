from wagtail.admin.forms import WagtailAdminModelForm

from ..forms import OrderModelForm


class WagtailOrderModelForm(OrderModelForm, WagtailAdminModelForm):
    pass
