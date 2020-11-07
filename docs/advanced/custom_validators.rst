.. _address-validation:

##############################
Custom validators & formatters
##############################

A list of validators and formatters that can be overridden in Salesman.

Address validator
=================

During the checkout process, both the *shipping* and *billing* addresses can be specified.
The default address validator is set to :func:`salesman.checkout.utils.validate_address`
that simply makes both address fields required to be entered by the customer.

This behavior can be overridden by providing a dotted path in ``SALESMAN_ADDRESS_VALIDATOR``
setting that points to your custom validator function.

.. tip::

    To validate a specific address format split the text by ``\n`` character and validate each line.

.. literalinclude:: /../salesman/checkout/utils.py
    :pyobject: validate_address

Your custom validator should accept a text ``value`` and return the validated version.
It also receives a ``context`` dictionary with additional context data like ``request``,
a ``basket`` object and ``address`` type (set to either *shipping* or *billing*).


Extra validator
===============

Both the basket and basket item objects have an ``extra`` JSON field to store additional
information that can be changed or updated via the API. By default no validation is enforced
through a placeholder :func:`salesman.basket.utils.validate_extra` function.

You can add custom validation by providing a dotted path in ``SALESMAN_EXTRA_VALIDATOR``
setting that points to your custom validator function.

.. literalinclude:: /../salesman/basket/utils.py
    :pyobject: validate_extra

Your custom validator should accept a dictionary ``value`` and return the validated version.
It also receives a ``context`` dictionary with additional context data like  ``request``,
a ``basket`` object and ``basket_item`` in case validation is happening on the basket item.


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
