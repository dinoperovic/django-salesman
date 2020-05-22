# models.py
from django.db import models


class Product(models.Model):
    """
    Simple single type product.
    """

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    def __str__(self):
        return self.name

    def get_price(self, request):
        return self.price

    @property
    def code(self):
        return str(self.id)


class Phone(models.Model):
    """
    Group product example, holds Phone product common data.
    Used for display, PhoneVariant is the actual product that gets added to basket.
    """

    name = models.CharField(max_length=255)
    base_price = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class PhoneVariant(models.Model):
    """
    Variant product for Phone group.
    """

    COLORS = [
        ('black', "Black"),
        ('silver', "Silver"),
        ('gold', "Gold"),
    ]
    CAPACITIES = [
        ('64', "64G"),
        ('128', "128G"),
        ('256', "256G"),
    ]

    phone = models.ForeignKey(Phone, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)

    # Variant data
    color = models.CharField(max_length=50, choices=COLORS, default=COLORS[0][0])
    capacity = models.CharField(
        max_length=50, choices=CAPACITIES, default=CAPACITIES[0][0]
    )

    def __str__(self):
        return self.name

    def get_price(self, request):
        if self.price is None:
            return self.phone.base_price
        return self.price

    @property
    def name(self):
        return f'{self.phone} - {self.color} {self.capacity}'

    @property
    def code(self):
        return str(self.id)


class InvalidProduct(models.Model):
    """
    Dummy product model with no attributes for testing.
    """
