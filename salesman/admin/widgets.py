from django import forms

from salesman.conf import app_settings

EMPTY_CHOICE = ('', '---------')


class OrderStatusSelect(forms.Select):
    """
    Status widget with order status choices.
    """

    # Bound by modelform.
    order = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = app_settings.SALESMAN_ORDER_STATUS.choices

    def create_option(self, name, value, *args, **kwargs):
        option = super().create_option(name, value, *args, **kwargs)

        # Disable options that are not specified in status transitions.
        transitions = app_settings.SALESMAN_ORDER_STATUS.get_transitions()
        statuses = [status for status in app_settings.SALESMAN_ORDER_STATUS]
        current = self.order.status if self.order else None
        if value != current and value not in transitions.get(current, statuses):
            option['attrs']['disabled'] = True
        return option


class PaymentSelect(forms.Select):
    """
    Payment widget with payment method choices.
    """

    def __init__(self, *args, **kwargs):
        from salesman.checkout.payment import payment_methods_pool

        super().__init__(*args, **kwargs)
        self.choices = [EMPTY_CHOICE] + payment_methods_pool.get_choices()
