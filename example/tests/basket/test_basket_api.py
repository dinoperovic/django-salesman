import pytest
from django.urls import reverse
from rest_framework.settings import api_settings
from rest_framework.test import APIClient

from salesman.basket.api import BasketViewSet
from salesman.basket.models import BasketItem
from shop.models import Product


@pytest.mark.django_db
def test_basket_api():
    url = reverse('salesman-basket-list')
    client = APIClient()

    # test view name
    view = BasketViewSet()
    view.name = "Basket List"
    assert view.get_view_name() == "Basket"
    view.name = "Basket Instance"
    assert view.get_view_name() == "Basket Item"
    view.name = ""
    assert view.get_view_name() == ""

    # test basket item create
    product = Product.objects.create(name="Test")
    data = {
        'product_type': 'shop.Product',
        'product_id': product.id,
        'quantity': 2,
        'extra': {'test': 1},
    }
    response = client.post(url, data, format='json')
    data['ref'] = '1-new'
    response = client.post(url, data, format='json')
    assert response.status_code == 201
    item_ref = response.json()['ref']

    # test wrong product id
    data['product_id'] = 13
    response = client.post(url, data, format='json')
    assert response.status_code == 400
    assert api_settings.NON_FIELD_ERRORS_KEY in response.json()

    # test basket list
    response = client.get(url)
    assert response.status_code == 200
    assert 'total' in response.json()
    assert len(response.json()['items']) == 2

    # test basket item detail
    response = client.get(reverse('salesman-basket-detail', args=[item_ref]))
    assert response.status_code == 200
    assert 'total' in response.json()

    # test basket item update
    data = dict(quantity=7, extra={'y': 2})
    response = client.put(
        reverse('salesman-basket-detail', args=[item_ref]), data, format='json'
    )
    assert response.status_code == 200
    assert response.json()['extra']['y'] == 2
    assert response.json()['quantity'] == 7

    # test basket count
    response = client.get(reverse('salesman-basket-count'))
    assert response.json()['count'] == 2

    # test basket quantity
    response = client.get(reverse('salesman-basket-quantity'))
    assert response.json()['quantity'] == 9

    # test basket extra
    response = client.get(reverse('salesman-basket-extra'))
    assert response.status_code == 200
    assert 'extra' in response.json()
    data = dict(extra={'x': 1})
    response = client.put(reverse('salesman-basket-extra'), data, format='json')
    assert response.status_code == 200
    assert response.json()['extra']['x'] == 1

    # test basket destroy item
    response = client.delete(reverse('salesman-basket-detail', args=[item_ref]))
    assert response.status_code == 204
    assert BasketItem.objects.count() == 1

    # test basket clear
    response = client.post(reverse('salesman-basket-clear'))
    assert response.status_code == 200
    assert BasketItem.objects.count() == 0

    # test basket delete
    basket_id = response.json()['id']
    response = client.delete(url)
    assert response.status_code == 204
    response = client.get(url)
    assert response.json()['id'] == basket_id + 1
