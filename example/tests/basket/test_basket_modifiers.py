import pytest
from django.core.exceptions import ImproperlyConfigured

from salesman.basket.modifiers import BasketModifier, BasketModifiersPool
from salesman.conf import app_settings
from salesman.core.utils import get_salesman_model
from shop.models import Product

Basket = get_salesman_model('Basket')
BasketItem = get_salesman_model('BasketItem')


class DummyModifier(BasketModifier):
    identifier = 'dummy'


class ModifierWithoutIdentifier(BasketModifier):
    pass


class DuplicateIdentifierModifier(BasketModifier):
    identifier = 'dummy'


@pytest.mark.django_db
def test_modifier_add_extra_row(rf):
    request = rf.get('/')
    modifier = DummyModifier()
    basket = Basket.objects.create()
    product = Product.objects.create(name="Test", price=30)
    basket.add(product)
    basket.update(request)
    item = basket.get_items()[0]
    assert basket.total == 27  # 10% discount modifier is already active
    modifier.add_extra_row(item, request, label="Item label", amount=10.5, charge=False)
    assert item.total == 30
    modifier.add_extra_row(basket, request, label="Label", amount=10, extra={'test': 1})
    data = basket.extra_rows['dummy'].data
    assert data['label'] == "Label"
    assert data['amount'] == "10.00"
    assert data['extra']['test'] == 1
    assert basket.total == 37


def test_basket_modifiers_pool(settings):
    base_modifiers = ['tests.basket.test_basket_modifiers.DummyModifier']
    settings.SALESMAN_BASKET_MODIFIERS = base_modifiers
    modifiers = BasketModifiersPool().get_modifiers()
    assert len(modifiers) == 1
    del app_settings.SALESMAN_BASKET_MODIFIERS
    with pytest.raises(ImproperlyConfigured):
        settings.SALESMAN_BASKET_MODIFIERS = base_modifiers + [
            'tests.basket.test_basket_modifiers.ModifierWithoutIdentifier'
        ]
        BasketModifiersPool().get_modifiers()
        del app_settings.SALESMAN_BASKET_MODIFIERS
    with pytest.raises(ImproperlyConfigured):
        settings.SALESMAN_BASKET_MODIFIERS = base_modifiers + [
            'tests.basket.test_basket_modifiers.DuplicateIdentifierModifier'
        ]
        BasketModifiersPool().get_modifiers()
        del app_settings.SALESMAN_BASKET_MODIFIERS
