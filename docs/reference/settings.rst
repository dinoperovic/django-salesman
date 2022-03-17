.. _reference-settings:

########
Settings
########

A reference for Salesman's settings module located at ``salesman/conf.py``.

To use it in project:

.. code:: python

    from salesman.conf import app_settings

    format_price = app_settings.SALESMAN_PRICE_FORMATTER


.. autoclass:: salesman.conf.DefaultSettings
    :members:

.. autoattribute:: salesman.conf.app_settings
