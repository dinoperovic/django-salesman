from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SalesmanCoreApp(AppConfig):
    name = 'salesman.core'
    label = 'salesmancore'
    verbose_name = _("Salesman Core")
