.. _reference-checkout:

########
Checkout
########

Checkout reference.

Payment
=======

To use the payment methods:

.. code:: python

    from salesman.checkout.payment import payment_methods_pool

    basket_payments = payment_methods_pool.get_payments('basket')
    order_payments = payment_methods_pool.get_payments('order')

    payment = payment_methods_pool.get_payment('pay-in-advance')

.. automodule:: salesman.checkout.payment
    :members:

Serializers
===========

.. automodule:: salesman.checkout.serializers
    :members:

Utils
=====

.. automodule:: salesman.checkout.utils
    :members:

Views
=====

.. automodule:: salesman.checkout.views
    :members:
