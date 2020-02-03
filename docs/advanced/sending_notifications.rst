.. _sending-notifications:

#####################
Sending notifications
#####################

Most of the time you'll want to notify customers via email when an order
has been made or it's status has changed. For that scenario Salesman provides a
:attr:`salesman.orders.signals.status_changed` signal that you can use. Eg:

.. note::

    For this example we assume your custom app is named ``shop``.

.. code:: python

    # signals.py
    from django.dispatch import receiver
    from django.core.mail import send_mail
    from django.conf import settings

    from salesman.orders.signals import status_changed


    @receiver(status_changed)
    def send_notification(sender, order, new_status, old_status, **kwargs):
        """
        Send notification to customer when order is completed.
        """
        if new_status == order.statuses.COMPLETED:
            subject = f"Order '{order}' is completed"
            message = "Thank you for shopping with Salesman!"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.email])

Make sure you import your signals in your app's ready function to have them registered:

.. code:: python

    # apps.py
    from django.apps import AppConfig


    class ShopApp(AppConfig):
        name = 'shop'

        def ready(self):
            import shop.signals


.. code:: python

    # __init__.py
    default_app_config = 'shop.apps.ShopApp'


Read more about listening to signals in Django's
`docs <https://docs.djangoproject.com/en/3.0/topics/signals/#listening-to-signals>`_.
