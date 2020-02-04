.. _checkout-and-payment:

##################
Checkout & payment
##################

To enable basket checkout you need to define a payment method in ``SALESMAN_PAYMENT_METHODS`` setting
which accepts a list of dotted paths to :class:`salesman.checkout.payment.PaymentMethod` classes.

.. note::

    For this example we assume your custom app is named ``shop``.

.. raw:: html

    <h3>1. Create payment method</h3>

First create your custom payment method. Payment methods are required to specify a ``label`` and
a unique ``identifier`` property on class. To enable payment for the basket you should also
override the :meth:`salesman.checkout.payment.PaymentMethod.basket_payment` method. Eg:

.. code:: python

    # payment.py
    from salesman.checkout.payment import PaymentMethod
    from salesman.orders.models import Order


    class PayInAdvance(PaymentMethod):
        """
        Payment method that requires advance payment via bank account.
        """
        identifier = 'pay-in-advance'
        label = 'Pay in advance'

        def basket_payment(self, basket, request):
            order = Order.objects.create_from_basket(basket, request, status='HOLD')
            basket.delete()
            return f'/success/?token={order.token}'

.. raw:: html

    <h3>2. Register payment method</h3>

Then register your payment method in ``settings.py``:

.. code:: python

    SALESMAN_PAYMENT_METHODS = [
        'shop.payment.PayInAdvance',
    ]

Now you can make a basket purchase through the :http:post:`/checkout/` request
with ``payment_method`` set to ``pay-in-advance``.

For more information about payment methods see :ref:`payment_methods`.
