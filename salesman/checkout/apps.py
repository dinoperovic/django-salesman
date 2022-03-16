from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SalesmanCheckoutApp(AppConfig):
    name = 'salesman.checkout'
    label = 'salesmancheckout'
    verbose_name = _("Salesman Checkout")
