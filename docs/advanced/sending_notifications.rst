.. _sending-notifications:

#####################
Sending notifications
#####################

Most of the time you'll want to notify customers via email when an order
has been made or its status has changed. For that scenario, Salesman provides a
:attr:`salesman.orders.signals.status_changed` signal that you can use. Eg:

.. note::

    For this example, we assume your custom app is named ``shop``.

.. literalinclude:: /../example/shop/signals.py

Make sure you import your signals in your app's ready function to have them registered:

.. literalinclude:: /../example/shop/apps.py
.. literalinclude:: /../example/shop/__init__.py

Read more about listening to signals in Django's
`docs <https://docs.djangoproject.com/en/3.0/topics/signals/#listening-to-signals>`_.
