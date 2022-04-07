import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from salesman.core.utils import get_salesman_model
from shop.models import Product

Order = get_salesman_model("Order")
OrderItem = get_salesman_model("OrderItem")
OrderPayment = get_salesman_model("OrderPayment")


@pytest.mark.django_db
def test_order_views(django_user_model):
    url = reverse("salesman-order-list")
    client = APIClient()
    # create dummy data
    user = django_user_model.objects.create_user(username="user", password="password")
    admin = django_user_model.objects.create_superuser(
        username="admin", password="password"
    )
    product = Product.objects.create(name="Test", price=100)
    order1 = Order.objects.create(
        ref="1", email="user@example.com", subtotal=70, total=80, user=user
    )
    order2 = Order.objects.create(
        ref="2", email="user@example.com", subtotal=70, total=80, user=user
    )
    order3 = Order.objects.create(
        ref="3", email="user@example.com", subtotal=70, total=80
    )
    OrderItem.objects.create(
        order=order1, product=product, unit_price=70, subtotal=70, total=70, quantity=1
    )
    OrderItem.objects.create(
        order=order2,
        product_data={"name": "Test data"},
        unit_price=70,
        subtotal=70,
        total=70,
        quantity=1,
    )  # noqa
    # test queryset empty for non-authenticated user
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.json()) == 0
    # test access to user with token
    response = client.get(url + f"?token={order1.token}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["ref"] == "1"
    # test user access
    client.force_authenticate(user)
    response = client.get(url)
    assert len(response.json()) == 2
    assert response.json()[0]["ref"] == "2"
    assert response.json()[0]["items"][0]["product"]["name"] == "Test data"
    # test last order
    url = reverse("salesman-order-last")
    response = client.get(url)
    assert response.status_code == 200
    assert response.json()["ref"] == "2"  # last user order
    # test last order with token
    client.force_authenticate(None)
    response = client.get(url)
    assert response.status_code == 404
    response = client.get(url + f"?token={order3.token}")
    assert response.json()["ref"] == order3.ref
    # test admin user access
    response = client.get(reverse("salesman-order-all"))
    assert response.status_code == 403
    client.force_authenticate(admin)
    response = client.get(reverse("salesman-order-all"))
    assert response.status_code == 200
    assert len(response.json()) == Order.objects.count()

    # test update order (status)
    url = reverse("salesman-order-status", args=[order1.ref])
    # test update order - no access for user
    client.force_authenticate(user)
    response = client.get(url)
    assert response.status_code == 403
    response = client.put(url, {"status": "CREATED"})
    assert response.status_code == 403
    # test update order - admin user can update
    client.force_authenticate(admin)
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.json()["status_transitions"]) == len(Order.Status)
    response = client.put(url, {"status": "CREATED"})
    assert response.status_code == 200
    assert response.json()["status"] == "CREATED"

    # test pay order
    # test pay order - invalid payent_method
    client.force_authenticate(user)
    response = client.post(
        reverse("salesman-order-pay", args=[order1.ref]), {"payment_method": "invalid"}
    )
    assert response.status_code == 400
    # test pay order - get payment methods
    response = client.get(reverse("salesman-order-pay", args=[order1.ref]))
    assert response.status_code == 200
    assert len(response.json()["payment_methods"]) == 2
    # test pay order - invalid order status
    order1.status = order1.Status.NEW
    order1.save(update_fields=["status"])
    url = reverse("salesman-order-pay", args=[order1.ref])
    response = client.post(url, {"payment_method": "dummy"})
    assert response.status_code == 400
    order1.status = order1.Status.CREATED
    order1.save(update_fields=["status"])
    # test pay order - success
    response = client.post(url, {"payment_method": "dummy"})
    assert response.status_code == 200
    # test pay order - raise payment error
    response = client.post(url + "?raise_error=1", {"payment_method": "dummy"})
    assert response.status_code == 402
    assert "detail" in response.json()
    # test pay order - already paid
    OrderPayment.objects.create(
        order=order1, amount=order1.total, transaction_id=1, payment_method="dummy"
    )
    order1.status = order1.Status.CREATED
    order1.save(update_fields=["status"])
    response = client.post(url, {"payment_method": "dummy"})
    assert response.status_code == 400

    # test refund order
    OrderPayment.objects.create(
        order=order1, amount=order1.total, transaction_id=2, payment_method="dummy2"
    )
    url = reverse("salesman-order-refund", args=[order1.ref])
    # test refund order - not admin
    response = client.post(url)
    assert response.status_code == 403
    client.force_authenticate(admin)
    # test refund order - partially refunded
    response = client.post(url)
    assert response.status_code == 206
    assert len(response.json()["refunded"]) == 1
    assert len(response.json()["failed"]) == 1
    # test refund order - success
    p = order1.payments.first()
    p.payment_method = "dummy2"
    p.save(update_fields=["payment_method"])
    response = client.post(url)
    assert response.status_code == 200
    assert len(response.json()["refunded"]) == 2
    # test refund order - alerady refunded
    response = client.post(url)
    assert response.status_code == 400
