.. _api-orders:

######
Orders
######

Api docs for Orders.

.. http:get:: /orders/

   Get orders for logged in user.

.. http:get:: /orders/last/

    Show last customer order.

   :query token: Token to get order when user is not logged in

.. http:get:: /orders/all/

    Show all orders to the admin user, only available if staff user.

.. http:get:: /orders/(str:ref)/

    Get order.

    .. sourcecode:: json

        {
            "id": 1,
            "url": "http://localhost:8000/api/orders/2020-00001/",
            "ref": "2020-00001",
            "token": "2ObSviY4oVR-2qa-wTsJ6AsYQWuzscb-jCpv80ueclM",
            "status": "HOLD",
            "status_display": "Hold",
            "date_created": "2020-01-10T14:17:24.099278Z",
            "date_updated": "2020-01-10T14:17:24.103430Z",
            "is_paid": false,
            "user": null,
            "email": "user@example.com",
            "billing_address": "Test address",
            "shipping_address": "Test address",
            "subtotal": "33.00",
            "extra_rows": [],
            "total": "33.00",
            "amount_paid": "0.00",
            "amount_outstanding": "33.00",
            "extra": {},
            "items": [
                {
                    "id": 1,
                    "product_type": "shop.Product",
                    "product_id": 1,
                    "product": {
                        "name": "Product",
                        "code": "1"
                    },
                    "unit_price": "33.00",
                    "quantity": 1,
                    "subtotal": "33.00",
                    "extra_rows": [],
                    "total": "33.00",
                    "extra": {}
                }
            ],
            "payments": [],
            "notes": []
        }

    :param ref: order ref
    :type ref: str
    :query token: Token to get order when user is not logged in

.. http:get:: /orders/(str:ref)/status/

    Show order status with transitions, only available if staff user.

    .. sourcecode:: json

        {
            "status": "HOLD",
            "status_display": "Hold",
            "status_transitions": [
                {
                    "value": "NEW",
                    "label": "New",
                    "error": "Can't change order with status 'Hold' to 'New'."
                },
                {
                    "value": "CREATED",
                    "label": "Created",
                    "error": "Can't change order with status 'Hold' to 'Created'."
                },
                {
                    "value": "HOLD",
                    "label": "Hold",
                    "error": null
                },
                {
                    "value": "FAILED",
                    "label": "Failed",
                    "error": null
                },
                {
                    "value": "CANCELLED",
                    "label": "Cancelled",
                    "error": null
                },
                {
                    "value": "PROCESSING",
                    "label": "Processing",
                    "error": null
                },
                {
                    "value": "SHIPPED",
                    "label": "Shipped",
                    "error": "Can't change order with status 'Hold' to 'Shipped'."
                },
                {
                    "value": "COMPLETED",
                    "label": "Completed",
                    "error": "Can't change order with status 'Hold' to 'Completed'."
                },
                {
                    "value": "REFUNDED",
                    "label": "Refunded",
                    "error": "Can't change order with status 'Hold' to 'Refunded'."
                }
            ]
        }

    :param ref: order ref
    :type ref: str

.. http:put:: /orders/(str:ref)/status/

    Change order status, only available if staff user.

    .. sourcecode:: json

        {
            "status": "PROCESSING",
            "status_display": "Processing"
        }

    :param ref: order ref
    :type ref: str
    :jsonparam str status: new order status
    :statuscode 400: if supplied params are invalid

.. http:get:: /orders/(str:ref)/pay/

    List payment methods with :meth:`salesman.checkout.payment.PaymentMethod.order_payment`
    implemented. Show error message if it exist.

    .. sourcecode:: json

        {
            "payment_methods": [
                {
                    "identifier": "credit-card",
                    "label": "Credit Card",
                    "error": null
                }
            ]
        }

    :param ref: order ref
    :type ref: str
    :query token: Token to get order when user is not logged in

.. http:post:: /orders/(str:ref)/pay/

    Pay for order. Get redirect URL to either the next payment step
    or the order success page. Depending on the used payment method
    redirect to this URL.

    .. sourcecode:: json

        {
            "url": "https://credit-card-payment.com/?order=2020-00001&total=33.00"
        }

    :param ref: order ref
    :type ref: str
    :query token: Token to get order when user is not logged in
    :statuscode 400: if supplied params are invalid
    :statuscode 402: if payment error appears

.. http:post:: /orders/(str:ref)/refund/

    Refund all order payments, only available if staff user.

    .. sourcecode:: json

        {
            "refunded": [
                {
                    "amount": "33.00",
                    "transaction_id": "43ae45fa-6af8-4dcf-a854-b1f8245ec07b",
                    "payment_method": "credit-card",
                    "date_created": "2020-01-10T14:49:25.105242Z"
                }
            ],
            "failed": []
        }

    :param ref: order ref
    :type ref: str
    :statuscode 206: if some payments failed while refunding

