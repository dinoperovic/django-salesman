.. _adding-products:

###############
Adding products
###############

To add products to the basket they need be registered in ``SALESMAN_PRODUCT_TYPES``
dictionary setting with values formated as ``'app_name.Model': 'path.to.ModelSerializer'``.

.. note::

    For this example we assume your custom app is named ``shop``.

.. raw:: html

    <h3>1. Create product model</h3>

First create a product model. Requirements are that it implements ``get_price(self, request)``
method and has properties ``name`` and ``code``. Eg:

.. code:: python

    # models.py
    from django.db import models


    class Product(models.Model):
        name = models.CharField(max_length=255)
        price = models.DecimalField(max_digits=18, decimal_places=2)

        def get_price(self, request):
            return self.price

        @property
        def code(self):
            return str(self.pk)

.. raw:: html

    <h3>2. Create product serializer</h3>

Then create a serializer for the product. Eg:

.. code:: python

    # serializers.py
    from rest_framework import serializers

    from .models import Product


    class ProductSerializer(serializers.ModelSerializer):
        class Meta:
            model = Product
            fields = ['name', 'code']


.. raw:: html

    <h3>3. Register the product</h3>

Only thing left is to register it in ``settings.py``:

.. code:: python

    SALESMAN_PRODUCT_TYPES = {
        'shop.Product': 'shop.serializers.ProductSerializer',
    }

You can now add the product to the basket by sending a :http:post:`/basket/` request.
In your request you should include ``product_type`` with value ``shop.Product`` and ``product_id``
with product instance id as value.
