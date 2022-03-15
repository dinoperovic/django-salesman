# modifiers.py
from salesman.basket.modifiers import BasketModifier


class DiscountModifier(BasketModifier):
    """
    Apply 10% discount on entire basket.
    """

    identifier = 'discount'

    def process_basket(self, basket):
        if basket.count:
            amount = basket.subtotal / -10
            self.add_extra_row(basket, label="Discount 10%", amount=amount)


class SpecialTaxModifier(BasketModifier):
    """
    Add 10% tax on items with price grater than 99.
    """

    identifier = 'special-tax'

    def process_item(self, item):
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

    def process_basket(self, basket):
        if basket.count:
            self.add_extra_row(basket, label="Shipping", amount=30)
