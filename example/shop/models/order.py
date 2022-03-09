from salesman.orders.models import (
    BaseOrder,
    BaseOrderItem,
    BaseOrderNote,
    BaseOrderPayment,
)


class Order(BaseOrder):
    pass


class OrderItem(BaseOrderItem):
    pass


class OrderPayment(BaseOrderPayment):
    pass


class OrderNote(BaseOrderNote):
    pass
