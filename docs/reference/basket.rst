.. _reference-basket:

######
Basket
######

Basket reference.

Modifiers
=========

To use the modifiers:

.. code:: python

    from salesman.basket.modifiers import basket_modifiers_pool

    modifiers = basket_modifiers_pool.get_modifiers()


.. autoclass:: salesman.basket.modifiers.BasketModifier
    :members:
.. autoclass:: salesman.basket.modifiers.BasketModifiersPool
    :members:
.. autoattribute:: salesman.basket.modifiers.basket_modifiers_pool

Utils
=====

.. autofunction:: salesman.basket.utils.validate_extra

Models
======

.. autoclass:: salesman.basket.models.BasketManager
    :members:
.. autoclass:: salesman.basket.models.Basket
    :members: update, add, remove, clear, merge, get_items, count, quantity
.. autoclass:: salesman.basket.models.BasketItem
    :members: update, get_product_ref

Serializers
===========

.. autoclass:: salesman.basket.serializers.ProductField
.. autoclass:: salesman.basket.serializers.ExtraRowsField
.. autoclass:: salesman.basket.serializers.ExtraRowSerializer
.. autoclass:: salesman.basket.serializers.BasketItemSerializer
.. autoclass:: salesman.basket.serializers.BasketItemCreateSerializer
    :show-inheritance:
.. autoclass:: salesman.basket.serializers.BasketSerializer
.. autoclass:: salesman.basket.serializers.BasketExtraSerializer
    :show-inheritance:
