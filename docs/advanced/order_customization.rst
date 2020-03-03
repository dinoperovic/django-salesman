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

.. code:: python

    class OrderStatus(BaseOrderStatus):
        """
        Default order choices enum. Can be overriden by providing a
        dotted path to a class in ``SALESMAN_ORDER_STATUS`` setting.
        Required choices are NEW, CREATED, COMPLETED and REFUNDED.
        """

        NEW = 'NEW', _("New")  # Order with reference created, items are in the basket.
        CREATED = 'CREATED', _("Created")  # Created with items and pending payment.
        HOLD = 'HOLD', _("Hold")  # Stock reduced but still awaiting payment.
        FAILED = 'FAILED', _("Failed")  # Payment failed, retry is available.
        CANCELLED = 'CANCELLED', _("Cancelled")  # Cancelled by seller, stock increased.
        PROCESSING = 'PROCESSING', _("Processing")  # Payment confirmed, processing order.
        SHIPPED = 'SHIPPED', _("Shipped")  # Shipped to customer.
        COMPLETED = 'COMPLETED', _("Completed")  # Completed and received by customer.
        REFUNDED = 'REFUNDED', _("Refunded")  # Fully refunded by seller.

        @classmethod
        def get_payable(cls) -> list:
            """
            Returns default payable statuses.
            """
            return [cls.CREATED, cls.HOLD, cls.FAILED]

        @classmethod
        def get_transitions(cls) -> list:
            """
            Returns default status transitions.
            """
            return {
                'NEW': [cls.CREATED],
                'CREATED': [cls.HOLD, cls.FAILED, cls.CANCELLED, cls.PROCESSING],
                'HOLD': [cls.FAILED, cls.CANCELLED, cls.PROCESSING],
                'FAILED': [cls.CANCELLED, cls.PROCESSING],
                'CANCELLED': [],
                'PROCESSING': [cls.SHIPPED, cls.COMPLETED, cls.REFUNDED],
                'SHIPPED': [cls.COMPLETED, cls.REFUNDED],
                'COMPLETED': [cls.REFUNDED],
                'REFUNDED': [],
            }

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

    Eg. you could enforce a check that order is fully paid before it can be marked as *Completed*.

A default status transition validation is provided with :class:`salesman.orders.status.BaseOrderStatus`
class which checks that transition is available for the current order status:

.. code:: python

    @classmethod
    def validate_transition(cls, status: str, order: Order) -> None:
        """
        Validate a given status transition for the order.
        By default check status is defined in transitions.

        Args:
            status (str): New status
            order (Order): Order instance

        Raises:
            ValidationError: If transition not valid
        """
        transitions = cls.get_transitions().get(order.status, [status])
        transitions.append(order.status)
        if status not in transitions:
            current, new = cls[order.status].label, cls[status].label
            msg = _(f"Can't change order with status '{current}' to '{new}'.")
            raise ValidationError(msg)

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

.. code:: python

    def generate_ref(request: HttpRequest) -> str:
        """
        Default order reference generator function. Can be overriden by providing a
        dotted path to a function in ``SALESMAN_ORDER_REFERENCE_GENERATOR`` setting.

        Default format is ``{year}-{5-digit-increment}`` (eg. `2020-00001`).

        Args:
            request (HttpRequest): Django request

        Returns:
            str: New order reference
        """
        year = timezone.now().year
        last = Order.objects.filter(date_created__year=year, ref__isnull=False).first()
        increment = int(last.ref.split('-')[1]) + 1 if last and last.ref else 1
        return f'{year}-{increment:05d}'

Your custom function should accept Django's ``request`` object as a parameter.
