.. _api-checkout:

########
Checkout
########

Api docs for Checkout.

.. http:get:: /checkout/

    List payment methods with :meth:`salesman.checkout.payment.PaymentMethod.basket_payment`
    implemented. Show error message if it exist.

    .. sourcecode:: json

        {
            "payment_methods": [
                {
                    "identifier": "pay-in-advance",
                    "label": "Pay in advance",
                    "error": null
                }
            ]
        }

.. http:post:: /checkout/

    Process the checkout. Get redirect url to either the next payment step
    or the order success page. Depending on the used payment method
    redirect to this url.

    .. sourcecode:: json

        {
            "url": "http://localhost:8000/api/orders/last/?token=2ObSviY4oVR-2qa-wTsJ6AsYQWuzscb-jCpv80ueclM"
        }

    :jsonparam str email: customer email
    :jsonparam string shipping_address: shipping address text
    :jsonparam string billing_address: billing address text
    :jsonparam string payment_method: payment method used to purchase
    :statuscode 400: if supplied params are invalid
    :statuscode 402: if payment error appears
