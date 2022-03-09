import pytest

from salesman.core.models import JSONField
from salesman.core.utils import get_salesman_model

Basket = get_salesman_model('Basket')


@pytest.mark.django_db
def test_jsonfield():
    basket = Basket.objects.create()
    assert basket.extra == {}
    basket.extra = {'test': 1}
    basket.save(update_fields=['extra'])
    assert basket.extra['test'] == 1
    basket.extra['new'] = "new value"
    basket.save(update_fields=['extra'])
    assert basket.extra == {'test': 1, 'new': 'new value'}
    assert JSONField().to_python('{"test": 1}') == {'test': 1}
