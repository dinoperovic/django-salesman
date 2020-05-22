################
Basket modifiers
################

Sometimes we need to add extra charges or discounts to the basket and its items.
This is done using basket modifiers which allow for manipulation of both the items
individually and the basket itself. When a custom modifier is defined it can choose
to process the basket or item or both.

Modifiers are registered in ``SALESMAN_BASKET_MODIFIERS`` setting and should be formatted
as a list of dotted paths to a class extending :class:`salesman.basket.modifiers.BasketModifier`
class.

.. note::

    For this example, we assume your custom app is named ``shop``.

Create modifiers
================

A unique ``identifier`` property is required to be set on modifiers. To add extra rows to
basket or items individually use :meth:`salesman.basket.modifiers.BasketModifier.add_extra_row` method. Eg:

.. literalinclude:: /../example/shop/modifiers.py

Register modifiers
==================

Register modifiers in your ``settings.py``, ordering is preserved when processing:

.. code:: python

    SALESMAN_BASKET_MODIFIERS = [
        'shop.modifiers.DiscountModifier',
        'shop.modifiers.SpecialTaxModifier',
        'shop.modifiers.ShippingCostModifier',
    ]

Your basket will now contain extra rows when needed. They will appear as ``extra_rows`` list field
on both the basket and its items.
