import pytest
from django.db import transaction
from django.db.models.deletion import ProtectedError

from salesman.basket.models import BASKET_ID_SESSION_KEY, Basket, BasketItem
from shop.models import Phone, PhoneVariant, Product


@pytest.mark.django_db
def test_get_or_create_basket_from_request(rf, django_user_model):
    request = rf.get('/')

    # test session basket created
    basket, created = Basket.objects.get_or_create_from_request(request)
    assert created
    assert request.session[BASKET_ID_SESSION_KEY] == basket.id
    _, created = Basket.objects.get_or_create_from_request(request)
    assert not created

    # test user basket created
    request.user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    basket, created = Basket.objects.get_or_create_from_request(request)
    assert created
    assert Basket.objects.count() == 1  # session basket is merged and deleted
    assert basket.owner == request.user
    assert BASKET_ID_SESSION_KEY not in request.session
    _, created = Basket.objects.get_or_create_from_request(request)
    assert not created

    # test multiple baskets merge, 1 should be left
    Basket.objects.create(owner=request.user)
    basket, _ = Basket.objects.get_or_create_from_request(request)
    assert request.user.basket_set.count() == 1


@pytest.mark.django_db
def test_basket_str():
    basket = Basket()
    assert str(basket) == "(unsaved)"
    basket.save()
    assert str(basket) == "1"


@pytest.mark.django_db
def test_basket_update(rf):
    request = rf.get('/')
    basket, _ = Basket.objects.get_or_create_from_request(request)
    product = Product.objects.create(name="Test", price=30)
    basket.add(product, quantity=2)
    assert not hasattr(basket, 'extra_rows')
    assert not hasattr(basket, 'subtotal')
    assert not hasattr(basket, 'total')
    basket.update(request)
    total = 60
    total_with_modifiers = total - (
        total / 10
    )  # 10% discount modifier is already active
    assert basket.subtotal == total
    assert basket.total == total_with_modifiers
    assert len(basket.extra_rows) == 1


@pytest.mark.django_db
def test_basket_item_manipulation(rf):
    request = rf.get('/')
    basket, _ = Basket.objects.get_or_create_from_request(request)
    product = Product.objects.create(name="Test")

    # test add to basket
    item = basket.add(product)
    assert basket.count == 1
    assert item.product == product
    basket.add(product)
    assert basket.quantity == 2
    basket.add(product, ref="1-special")
    assert basket.count == 2
    assert basket.quantity == 3

    # test remove from basket
    basket.remove(item.ref)
    basket.get_items()  # trigger storing `_cached_items`.
    assert basket.count == 1
    assert basket.quantity == 1
    basket.remove('non-existant-ref')  # fail silently no item remove

    # test basket clear
    basket.clear()
    assert basket.count == basket.quantity == 0


@pytest.mark.django_db
def test_basket_merge(rf):
    request = rf.get('/')
    basket, _ = Basket.objects.get_or_create_from_request(request)
    product = Product.objects.create(name="Test")
    product_2 = Product.objects.create(name="Test #2")
    basket.add(product)
    basket_2 = Basket.objects.create()
    basket_2.add(product)
    basket_2.add(product_2)
    assert Basket.objects.count() == 2
    basket.merge(basket_2)
    assert Basket.objects.count() == 1
    assert basket.count == 2
    assert basket.quantity == 3


@pytest.mark.django_db
def test_basket_item(rf):
    request = rf.get('/')
    basket, _ = Basket.objects.get_or_create_from_request(request)
    product = Product.objects.create(name="Test")
    item = basket.add(product)

    # test save
    item.ref = None
    item.save(update_fields=['ref'])
    assert item.ref == BasketItem.get_product_ref(product) == 'shopproduct-1'
    assert str(item) == f"1x {product}"

    assert item.name == product.name
    assert item.code == product.code


@pytest.mark.django_db
def test_basket_item_update(rf):
    request = rf.get('/')
    basket, _ = Basket.objects.get_or_create_from_request(request)
    price = 30
    product = Product.objects.create(name="Test", price=price)
    basket.add(product)
    item = basket.get_items()[0]
    assert not hasattr(item, 'unit_price')
    assert not hasattr(item, 'subtotal')
    assert not hasattr(item, 'total')
    assert not hasattr(item, 'extra_rows')
    item.update(request)
    assert item.unit_price == price
    assert item.subtotal == price
    assert item.total == price
    assert len(item.extra_rows) == 0


@pytest.mark.django_db
def test_basket_item_protect(rf):
    request = rf.get('/')
    basket, _ = Basket.objects.get_or_create_from_request(request)
    price = 30
    product = Product.objects.create(name="Test", price=price)
    phone = Phone.objects.create(name="Phone")
    phone_product = PhoneVariant.objects.create(phone=phone)
    item = basket.add(product)
    basket.add(phone_product)
    with transaction.atomic():
        with pytest.raises(ProtectedError):
            product.delete()
    with transaction.atomic():
        with pytest.raises(ProtectedError):
            phone.delete()
    basket.remove(item.ref)
    product.delete()
