#################
Custom validators
#################

A list of validators that can be overridden in Salesman.


.. _address-validator:

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


.. _basket-item-validator:

Basket item validator
=====================

Custom basket item validation is possible through a custom validator function. By default no
extra validation is enforced through a placeholder :func:`salesman.basket.utils.validate_basket_item` function.

You can add custom validation by providing a dotted path in ``SALESMAN_BASKET_ITEM_VALIDATOR``
setting that points to your custom validator function.

.. tip::

    You can use this validator to check if an item can be added to the basket.
    If basket item instance in ``context['basket_item']`` is ``None``, a new item beeing added.


.. literalinclude:: /../salesman/basket/utils.py
    :pyobject: validate_basket_item

Your custom validator should accept a dictionary ``attrs`` value and return the validated version.
It also receives a ``context`` dictionary with additional context data like  ``request``,
a ``basket`` object and ``basket_item`` instance in case an existing item is validated.


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
