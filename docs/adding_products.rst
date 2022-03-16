.. _adding-products:

###############
Adding products
###############

To add products to the basket they need to be registered in ``SALESMAN_PRODUCT_TYPES``
dictionary setting with values formatted as ``'app_name.Model': 'path.to.ModelSerializer'``.

.. note::
    For this example, we assume your custom app is named ``shop``.

.. raw:: html

    <h3>1. Create product models</h3>

First, create a product model. Requirements are that it implements ``get_price(self, request)``
method and has properties ``name`` and ``code``. Eg:

.. literalinclude:: /../example/shop/models/product.py
    :lines: 1-21

.. raw:: html

    <h3>2. Create product serializers</h3>

Then create a serializer for the product. Eg:

.. literalinclude:: /../example/shop/serializers.py
    :lines: 1-10

.. raw:: html

    <h3>3. Register the product types</h3>

The only thing left is to register it in ``settings.py``:

.. code:: python

    SALESMAN_PRODUCT_TYPES = {
        'shop.Product': 'shop.serializers.ProductSerializer',
    }

You can now add the product to the basket by sending a :http:post:`/basket/` request.
In your request, you should include ``product_type`` set as ``shop.Product`` and
``product_id`` with product instance id as the value.
