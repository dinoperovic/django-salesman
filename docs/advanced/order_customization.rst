.. _order_customization:

###################
Order customization
###################

This page documents different order customization methods.

Custom statuses
===============

Order statuses are defined using django's :meth:`django.db.models.TextChoices` enum class with
the default set to :class:`salesman.orders.status.OrderStatus` class.

You can change it by providing a dotted path in ``SALESMAN_ORDER_STATUS`` setting
that points to a class extending :class:`salesman.orders.status.BaseOrderStatus` class.

.. literalinclude:: /../salesman/orders/status.py
    :pyobject: OrderStatus

As seen in the default status class above, you must define statuses with names and values ``NEW``,
``CREATED``, ``COMPLETED`` and ``REFUNDED`` while others are customizable to your needs.

You can also optionally override :meth:`salesman.orders.status.BaseOrderStatus.get_payable` method that
returns a list of statuses from which an order is eligible for payment, and
:meth:`salesman.orders.status.BaseOrderStatus.get_transitions` method which limits status transitions
for an order.

Order Status enum can be access using :attr:`salesman.orders.models.BaseOrder.Status` class property.

Validate status transitions
---------------------------

You might want to validate certain status transitions for your orders. This is possible by
overriding the :meth:`salesman.orders.status.BaseOrderStatus.validate_transition` method.

.. tip::
    Eg. you could enforce a check that the order has been fully paid for before it can be marked
    as *Completed*, or even return and force a different status entirely.

A default status transition validation is provided with :class:`salesman.orders.status.BaseOrderStatus`
class which checks that transition is available for the current order status:

.. literalinclude:: /../salesman/orders/status.py
    :pyobject: BaseOrderStatus.validate_transition

.. note::
    To include base validation be sure to call ``super()`` when overriding validation.

Custom reference generator
==========================

Order reference is generated when a new order get's created and represents a unique identifier
for that order. By default reference is generated in a ``{year}-{5-digit-increment}`` format using
:func:`salesman.orders.utils.generate_ref` function.

You can change it by providing a dotted path in ``SALESMAN_ORDER_REFERENCE_GENERATOR`` setting that
points to a function that returns a unique reference string.

.. literalinclude:: /../salesman/orders/utils.py
    :pyobject: generate_ref

Your custom function should accept Django's ``request`` object as a parameter.

.. _custom-order-serializer:

Custom order serializer
=======================

You can override order serializer by providing a dotted path in ``SALESMAN_ORDER_SERIALIZER`` setting.
Optionally you can configure a separate order "summary" serializer with ``SALESMAN_ORDER_SUMMARY_SERIALIZER``
setting, otherwise the same order serializer is used. Default serializer for is set
to :class:`salesman.orders.serializers.OrderSerializer`.

You can also override the ``OrderSerializer.Meta.prefetched_fields`` property to optimize for any added
relations to your custom serializer.
