##############
In Development
##############

*TBA*

Added
-----

- Added :class:`salesman.core.typing.Product` protocol used to check product types.
- Added :meth:`salesman.orders.models.BaseOrder.get_items` to mirror the ``BaseBasket.get_items`` API.

Changed
-------

- Renamed ``DefaultSettings`` to ``AppSettings`` in config module.
- Use cached properties for settings that load objects.
- Renamed ``owner`` field on ``BaseBasket`` to ``user`` for consistency with ``BaseOrder``.
