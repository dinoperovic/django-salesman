# import pytest
# from django.utils.formats import date_format

# from salesman.admin import models, utils


# @pytest.mark.django_db
# def test_order(django_user_model):
#     order = models.Order.objects.create(ref="1", subtotal=100, total=120)
#     user = django_user_model.objects.create_user(username='user', password='password')

#     order.extra = {'test': 1}
#     order.extra_rows = [1, 2, 3]
#     order.save()
#     assert order.extra_display() == utils.format_json({'test': 1})
#     assert order.extra_rows_display() == utils.format_json([1, 2, 3])
#     assert order.date_created_display() == date_format(
#         order.date_created, format="DATETIME_FORMAT"
#     )
#     assert order.date_updated_display() == date_format(
#         order.date_updated, format="DATETIME_FORMAT"
#     )
#     assert order.is_paid_display() == order.is_paid

#     # Customer display
#     assert order.customer_display() == '-'
#     order.user = user
#     order.save(update_fields=["user"])
#     assert order.customer_display().startswith(f'<a href="/admin/auth/user/{user.id}')
#     assert order.customer_display(context={'wagtail': True}).startswith(
#         f'<a href="/cms/users/{user.id}'
#     )

#     result = order.shipping_address.replace('\n', '<br>') or '-'
#     assert order.shipping_address_display() == result
#     result = order.billing_address.replace('\n', '<br>') or '-'
#     assert order.billing_address_display() == result
#     assert order.subtotal_display() == '100.00'
#     assert order.total_display() == '120.00'
#     assert order.amount_paid_display() == '0.00'
#     assert order.amount_outstanding_display() == '120.00'


# @pytest.mark.django_db
# def test_order_item():
#     order = models.Order.objects.create(ref="1", subtotal=100, total=120)
#     item = models.OrderItem.objects.create(
#         order=order, unit_price=50, subtotal=100, total=120, quantity=2
#     )
#     item.product_data = {'name': "Prod", "code": "1"}
#     item.extra = {'test': 1}
#     item.extra_rows = [1, 2, 3]
#     item.save()
#     result = utils.format_json({'name': "Prod", "code": "1"})
#     assert item.product_data_display() == result
#     assert item.extra_display() == utils.format_json({'test': 1})
#     assert item.extra_rows_display() == utils.format_json([1, 2, 3])
#     assert item.unit_price_display() == '50.00'
#     assert item.subtotal_display() == '100.00'
#     assert item.total_display() == '120.00'


# @pytest.mark.django_db
# def test_order_payment():
#     order = models.Order.objects.create(ref="1", subtotal=100, total=120)
#     pay = models.OrderPayment.objects.create(
#         order=order, amount=120, transaction_id="1"
#     )
#     assert pay.amount_display() == '120.00'
#     assert pay.date_created_display() == date_format(
#         pay.date_created, format="DATETIME_FORMAT"
#     )
