import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from salesman.checkout.api import CheckoutViewSet
from shop.models import Product


@pytest.mark.django_db
def test_checkout_api(settings):
    url = reverse('salesman-checkout-list')
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
    assert len(response.json()['payment_methods']) == 1

    # test empty basket error
    valid_data = {
        'email': 'user@example.com',
        'shipping_address': "Test",
        'billing_address': "Test",
        'payment_method': 'dummy',
    }
    response = client.post(url, valid_data)
    assert response.status_code == 400

    # add item to cart
    response = client.post(
        reverse('salesman-basket-list'),
        {'product_type': 'shop.Product', 'product_id': product.id},
    )
    assert response.status_code == 201

    # test no addresses specified error
    response = client.post(
        url, {'email': 'user@example.com', 'payment_method': 'dummy'}
    )
    assert response.status_code == 400

    # test process new checkout
    response = client.post(url, valid_data)
    assert response.status_code == 201
    assert 'url' in response.json()

    # test `PaymentError` caught
    client.post(
        reverse('salesman-basket-extra'), {'extra': {'raise_error': 1}}, format='json'
    )
    response = client.post(url, valid_data)
    assert response.status_code == 402
    assert response.json()['detail'] == 'Dummy payment error'
