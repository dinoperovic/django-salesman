import pytest
from django.utils.timezone import now

from salesman.core.utils import get_salesman_model
from salesman.orders.utils import generate_ref

Order = get_salesman_model("Order")


@pytest.mark.django_db
def test_generate_ref(rf):
    request = rf.get("/")
    year = now().year
    ref = generate_ref(request)
    assert ref == f"{year}-00001"
    Order.objects.create(ref=ref)
    ref2 = generate_ref(request)
    assert ref2 == f"{year}-00002"
