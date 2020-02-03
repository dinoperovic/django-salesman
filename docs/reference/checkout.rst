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

    payment = payment_methods_pool.get_payments('pay-in-advance')


.. autoclass:: salesman.checkout.payment.PaymentError
.. autoclass:: salesman.checkout.payment.PaymentMethod
    :members:
.. autoclass:: salesman.checkout.payment.PaymentMethodsPool
    :members:
.. autoattribute:: salesman.checkout.payment.payment_methods_pool

Utils
=====

.. autofunction:: salesman.checkout.utils.validate_address

Serializers
===========

.. autoclass:: salesman.checkout.serializers.PaymentMethodSerializer
.. autoclass:: salesman.checkout.serializers.CheckoutSerializer
