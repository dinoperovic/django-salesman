.. _reference-orders:

######
Orders
######

Orders reference.

Status
======

.. autoclass:: salesman.orders.status.BaseOrderStatus
.. automethod:: salesman.orders.status.BaseOrderStatus.get_payable
.. automethod:: salesman.orders.status.BaseOrderStatus.get_transitions
.. automethod:: salesman.orders.status.BaseOrderStatus.validate_transition
.. autoclass:: salesman.orders.status.OrderStatus

Utils
=====

.. autofunction:: salesman.orders.utils.generate_ref

Signals
=======

.. autoproperty:: salesman.orders.signals.status_changed

Models
======

.. autoclass:: salesman.orders.models.OrderManager
    :members:
.. autoclass:: salesman.orders.models.Order
    :members: pay, populate_from_basket, status_display, statuses, amount_paid, amount_outstanding, is_paid, get_statuses
.. autoclass:: salesman.orders.models.OrderItem
    :members: name, code
.. autoclass:: salesman.orders.models.OrderPayment
    :members: get_payment_method, payment_method_display
.. autoclass:: salesman.orders.models.OrderNote

Serializers
===========

.. autoclass:: salesman.orders.serializers.OrderItemSerializer
.. autoclass:: salesman.orders.serializers.OrderPaymentSerializer
.. autoclass:: salesman.orders.serializers.OrderNoteSerializer
.. autoclass:: salesman.orders.serializers.OrderSerializer
.. autoclass:: salesman.orders.serializers.StatusTransitionSerializer
.. autoclass:: salesman.orders.serializers.OrderStatusSerializer
.. autoclass:: salesman.orders.serializers.OrderPaySerializer
.. autoclass:: salesman.orders.serializers.OrderRefundSerializer
