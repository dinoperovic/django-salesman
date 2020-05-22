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

.. note::

    Reference generators function output will be *slugified*.

.. literalinclude:: /../salesman/orders/utils.py
    :pyobject: generate_ref

Your custom function should accept Django's ``request`` object as a parameter.
