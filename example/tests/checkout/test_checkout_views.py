import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from salesman.checkout.views import CheckoutViewSet
from salesman.core.utils import get_salesman_model
from shop.models import Product

Order = get_salesman_model("Order")


@pytest.mark.django_db
def test_checkout_views(settings, django_user_model):
    url = reverse("salesman-checkout-list")
    client = APIClient()

    # test view name / empty queryset
    view = CheckoutViewSet()
    view.name = "Checkout List"
    assert view.get_view_name() == "Checkout"
    view.name = ""
    assert view.get_view_name() == ""
    assert not view.get_queryset()

    # create dummy data
    product = Product.objects.create(name="Test", price=100)

    # test get payment methods
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.json()["payment_methods"]) == 1

    # test empty basket error
    valid_data = {
        "email": "user@example.com",
        "shipping_address": "Test",
        "billing_address": "Test",
        "payment_method": "dummy",
        "extra": {"test": 1},
    }
    response = client.post(url, valid_data, "json")
    assert response.status_code == 400

    # add item to cart
    response = client.post(
        reverse("salesman-basket-list"),
        {"product_type": "shop.Product", "product_id": product.id},
    )
    assert response.status_code == 201

    # test no addresses specified error
    response = client.post(
        url, {"email": "user@example.com", "payment_method": "dummy"}
    )
    assert response.status_code == 400

    # test process new checkout
    response = client.post(url, valid_data, "json")
    assert response.status_code == 201
    assert "url" in response.json()

    # test created order
    order = Order.objects.first()
    assert order.email == valid_data["email"]
    assert order.shipping_address == valid_data["shipping_address"]
    assert order.billing_address == valid_data["billing_address"]
    assert order.extra["test"] == valid_data["extra"]["test"]

    # test `PaymentError` caught
    client.put(reverse("salesman-basket-extra"), {"extra": {"raise_error": 1}}, "json")
    response = client.post(url, valid_data, "json")
    assert response.status_code == 402
    assert response.json()["detail"] == "Dummy payment error"

    # add item to cart
    response = client.post(
        reverse("salesman-basket-list"),
        {"product_type": "shop.Product", "product_id": product.id},
    )

    # test anonymous user checkout is not allowed
    setattr(settings, "SALESMAN_ALLOW_ANONYMOUS_USER_CHECKOUT", False)
    response = client.get(url)
    assert response.status_code == 403
    response = client.post(url, valid_data, "json")
    assert response.status_code == 403

    # test anonymous user checkout is not allowed but authorized
    user = django_user_model.objects.create_user(username="user", password="password")
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200
    response = client.post(url, valid_data, "json")
    assert response.status_code == 201
