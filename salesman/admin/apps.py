from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SalesmanAdminApp(AppConfig):
    name = 'salesman.admin'
    label = 'salesman'
    verbose_name = _("Salesman")
