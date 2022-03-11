#################
Custom formatters
#################

A list of validators and formatters that can be overridden in Salesman.


.. _price-formatter:

Price formatter
===============

Displaying prices in Salesman is controlled using a price formatter function.
The default formatter function is set to :func:`salesman.core.utils.format_price` and returns
a value formated with two decimal places.

.. tip::
    Price formatter can be used *(among other things)* to display a price with a symbol or even a
    converted price to another currency based on the ``request`` that's received in the ``context``.

You can change the price formatter by providing a dotted path in ``SALESMAN_PRICE_FORMATTER`` setting
that points to your custom formatter function.

.. literalinclude:: /../salesman/core/utils.py
    :pyobject: format_price

Your custom function should accept a ``value`` argument of type ``Decimal`` and a ``context``
dictionary that contains additional render data like ``request`` and either the ``basket`` or
``order`` object. The function should return a formatted price as a string.


.. _admin-json-formatter:

Admin JSON formatter
====================

When displaying JSON data in admin, a formatter function is used. The default function
:func:`salesman.admin.utils.format_json` uses the ``Pygments`` library to create the
default JSON display. You can override the JSON formatter by providing a dotted path
to a function in ``SALESMAN_ADMIN_JSON_FORMATTER`` setting.

.. literalinclude:: /../salesman/admin/utils.py
    :pyobject: format_json

Your custom formatter should accept a dictionary ``value`` and return the HTML string.
It also receives a ``context`` dictionary with additional context. Either an ``order`` or
``order_item`` boolean will be passed in depending on the formatting location.
