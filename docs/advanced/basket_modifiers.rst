################
Basket modifiers
################

Sometimes we need to add extra charges or discounts to basket and it's items.
This is done using basket modifiers which allow for manipulation of both the items
individually and the basket itself. When a custom modifier is defined it can choose
to process the basket or item or both.

Modifiers are registered in ``SALESMAN_BASKET_MODIFIERS`` setting and should be formated
as a list of dotted paths to a class extending :class:`salesman.basket.modifiers.BasketModifier`
class.

.. note::

    For this example we assume your custom app is named ``shop``.

Create modifiers
================

A unique ``identifier`` property is required to be set on modifiers. To add extra rows to
basket or items individually use :meth:`salesman.basket.modifiers.BasketModifier.add_extra_row` method. Eg:

.. code:: python

    # modifiers.py
    from salesman.basket.modifiers import BasketModifier


    class DiscountModifier(BasketModifier):
        """
        Apply 10% discount on entire basket and 5% on items individually.
        """
        identifier = 'discount'

        def process_item(self, item, request):
            amount = item.total / -5
            self.add_extra_row(item, label="5% discount", amount=amount)

        def process_basket(self, basket, request):
            if basket.count:
                amount = basket.subtotal / -10
                self.add_extra_row(basket, label="10% discount", amount=amount)


    class SpecialTaxModifier(BasketModifier):
        """
        Add 10% tax on items with price grater than 99.
        """
        identifier = 'special-tax'

        def process_item(self, item, request):
            if item.total > 99:
                label = "Special tax"
                amount = item.total / 10
                extra = {'message': f"Price threshold is exceeded by {item.total - 99}"}
                self.add_extra_row(item, label, amount, extra)


    class ShippingCostModifier(BasketModifier):
        """
        Add flat shipping cost to the basket.
        """
        identifier = 'shipping-cost'

        def process_basket(self, basket, request):
            if basket.count:
                self.add_extra_row(basket, label="Shipping", amount=30)


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
on both the basket and it's items.
