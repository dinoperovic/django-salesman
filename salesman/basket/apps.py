from django.apps import AppConfig, apps
from django.db.models.deletion import ProtectedError
from django.db.models.signals import pre_delete
from django.utils.translation import gettext_lazy as _

from salesman.conf import app_settings
from salesman.core.utils import get_salesman_model


def protect_basket_items(sender, instance, **kwargs):
    """
    Protect against deletion of products already added to basket.
    """
    from django.contrib.contenttypes.models import ContentType

    BasketItem = get_salesman_model('BasketItem')
    content_type = ContentType.objects.get_for_model(sender)
    items = BasketItem.objects.filter(
        product_content_type=content_type, product_id=instance.id
    )
    if items.count():
        msg = f"Cannot delete the product '{instance}' because it is added to basket."
        raise ProtectedError(msg, items)


class SalesmanBasketApp(AppConfig):
    name = 'salesman.basket'
    label = 'salesmanbasket'
    verbose_name = _("Salesman Basket")

    def ready(self):
        # Connect `pre_delete` signal for each product model.
        for key in app_settings.SALESMAN_PRODUCT_TYPES.keys():
            app_label, model_name = key.split('.')
            model = apps.get_model(app_label, model_name)
            pre_delete.connect(protect_basket_items, sender=model, dispatch_uid=key)
