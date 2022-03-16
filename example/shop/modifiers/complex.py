# modifiers.py
import random

from salesman.basket.modifiers import BasketModifier


class ComplexModifier(BasketModifier):
    """
    Complex modifier that doesn't make much sense but is used to show advance usage.
    Refer to the BaskeModifier class to see available methods and call ordering.
    """

    identifier = 'complex'

    def setup_basket(self, basket, request):
        self.basket = basket

        # Set discount limit through the request.
        try:
            self.max_discounts = int(self.request.GET['max_discounts'])
        except (KeyError, ValueError):
            self.max_discounts = 0
        self.num_discounts = 0

        # Keep track of item with highest discount (amount, item).
        self.highest_discounted_item = (0, None)

    def setup_item(self, item, request):
        # Set a random tax on each item.
        item.tax_percent = random.choice([10, 20, 30])

    def process_item(self, item, request):
        # Apply a discount to item if max not reached.
        if self.num_discounts < self.max_discounts:
            amount = item.subtotal / -10
            self.add_extra_row(
                item,
                request,
                label="Discount 10%",
                amount=item.subtotal / -10,
                identifier='complex-discount',
            )
            self.num_discounts += 1

            # Set highest discounted item.
            if amount > self.highest_discounted_item[0]:
                self.highest_discounted_item = (amount, item)

        # Apply random tax after discount.
        tax_amount = item.total / item.tax_percent
        self.add_extra_row(
            item,
            request,
            label="Random tax",
            amount=tax_amount,
            identifier='complex-tax',
        )

    def finalize_item(self, item, request):
        # Set highest discounted item.
        amount = item.subtotal - item.total
        if amount > self.highest_discounted_item[0]:
            self.highest_discounted_item = (amount, item)

    def process_basket(self, basket, request):
        # Set special discount for highest discounted item.
        item = self.highest_discounted_item[1]
        if item:
            self.add_extra_row(
                item,
                request,
                label="Special discount 5%",
                amount=item.total / -5,
                extra={'diff': self.highest_discounted_item[0]},
                identifier='complex-special-discount',
            )

        # Add discount based on item quantity.
        if basket.quantity % 2 == 0:
            label = "Even discount 10%"
            amount = basket.subtotal / -10
        else:
            label = "Odd discount 13%"
            amount = basket.subtotal / -13

        self.add_extra_row(basket, request, label, amount)

    def finalize_basket(self, basket, request):
        # Set after all modifiers have processed the order.
        basket.extra['is_expensive'] = basket.total > 1000
