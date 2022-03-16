from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SalesmanOrdersApp(AppConfig):
    name = 'salesman.orders'
    label = 'salesmanorders'
    verbose_name = _("Salesman")
