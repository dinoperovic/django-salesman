import json

from django.db import models


class JSONField(models.TextField):
    """
    Simple JSON field.
    """

    description = 'JSON object'

    def __init__(self, *args, **kwargs):
        kwargs['null'] = False
        kwargs['default'] = {}
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        return json.loads(value)

    def to_python(self, value):
        return json.loads(value)

    def get_prep_value(self, value):
        value = value or {}
        if isinstance(value, dict):
            value = json.dumps(value)
        return value
