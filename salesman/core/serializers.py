from rest_framework import serializers

from salesman.conf import app_settings


class PriceField(serializers.CharField):
    """
    Price field used to display formated price whitin a serializer.
    """

    def to_representation(self, value):
        return app_settings.SALESMAN_PRICE_FORMATTER(value, context=self.context)
