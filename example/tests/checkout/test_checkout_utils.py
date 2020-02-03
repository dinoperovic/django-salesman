import pytest
from django.core.exceptions import ValidationError

from salesman.checkout import utils


def test_validate_address():
    with pytest.raises(ValidationError):
        assert utils.validate_address('')
    assert utils.validate_address('Test') == 'Test'
