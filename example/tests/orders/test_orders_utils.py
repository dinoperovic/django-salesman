import pytest
from django.utils.timezone import now

from salesman.orders.models import Order
from salesman.orders.utils import generate_ref


@pytest.mark.django_db
def test_generate_ref(rf):
    request = rf.get('/')
    year = now().year
    ref = generate_ref(request)
    assert ref == f'{year}-00001'
    Order.objects.create(ref=ref)
    ref2 = generate_ref(request)
    assert ref2 == f'{year}-00002'
