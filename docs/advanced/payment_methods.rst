.. _payment_methods:

###############
Payment methods
###############

This guide will show how a moderately complex payment method can be implemented. There are
two main components in Salesman's payment method interface:

- **Basket payment** is used during checkout where a basket get's converted to an order.
- **Order payment** is used when a payment is requested for an existing order.

You can optionally support either one or both methods in your payment method.

Payment methods are registered in ``SALESMAN_PAYMENT_METHODS`` setting and should be formatted
as a list of dotted paths to a class extending :class:`salesman.checkout.payment.PaymentMethod`
class. Defined payments are required to specify a ``label`` and a unique ``identifier`` property.

.. note::

    For this example, we assume your custom app is named ``shop``.

Validate payments
=================

Payment methods can be validated for both the basket and order instances. This is useful when
you wish to disable certain payments for a given request.

Default validations are included with base :class:`salesman.checkout.payment.PaymentMethod` class:

.. literalinclude:: /../salesman/checkout/payment.py
    :lines: 36-66

.. note::

    To include base validation be sure to call ``super()`` when overriding validation.

Basket validation example
-------------------------

In this example, we create an *on-delivery* payment method that is only valid when less
that 10 items are in the basket.

.. literalinclude:: /../example/shop/payment.py
    :lines: 1,4,3,10-11,12-13,35-60

Now only baskets with less than 10 items will be eligible for payment on delivery.

Credit card example
===================

A more complex example using an *off-site* dummy gateway.

.. literalinclude:: /../example/shop/payment.py
    :lines: 1-3,5-13,63-166

Register payments
=================

Enable payment methods by adding in ``settings.py``:

.. code:: python

    SALESMAN_PAYMENT_METHODS = [
        'shop.payment.PayOnDelivery',
        'shop.payment.CreditCardPayment',
    ]

You can now select those payment methods in checkout and order payment operations.
