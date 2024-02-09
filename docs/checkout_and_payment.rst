.. _checkout-and-payment:

##################
Checkout & payment
##################

To enable basket checkout you need to define a payment method in ``SALESMAN_PAYMENT_METHODS`` setting
which accepts a list of dotted paths to :class:`salesman.checkout.payment.PaymentMethod` classes.

.. note::

    For this example, we assume your custom app is named ``shop``.

.. raw:: html

    <h3>1. Create swappable order model</h3>

It is recommended to configure and setup all Salesman models as swappable even if it's not necessary at the beginning. This will future-proof your application in case you wish to add it later. This has to be done before the initial migrations are created. See :ref:`swappable_models`.

.. literalinclude:: /../example/shop/models/order.py

.. raw:: html

    <h3>2. Create payment method</h3>

First create your custom payment method. Payment methods are required to specify a ``label`` and
a unique ``identifier`` property on class. To enable payment for the basket you should also
override the :meth:`salesman.checkout.payment.PaymentMethod.basket_payment` method. Eg:

.. literalinclude:: /../example/shop/payment/advance.py

.. raw:: html

    <h3>3. Register payment method</h3>

Then register your payment method in ``settings.py``:

.. code:: python

    SALESMAN_PAYMENT_METHODS = [
        'shop.payment.PayInAdvance',
    ]

Now you can make a basket purchase through the :http:post:`/checkout/` request
with ``payment_method`` set to ``pay-in-advance``.

For more information about payment methods see :ref:`payment_methods`.

.. raw:: html

    <h3>Anonymous checkout</h3>

By default anonymous users can checkout. To prevent this behavior set ``SALESMAN_ALLOW_ANONYMOUS_USER_CHECKOUT = False``.

