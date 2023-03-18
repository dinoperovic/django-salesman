.. _swappable_models:

################
Swappable models
################

All Salesman models are swappable using Django's private swappable API used in
`Auth package <https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#substituting-a-custom-user-model>`_.
This allows for full control of Salesman models and makes adding new fields or features easier.
Swapped models must extend their "Base" versions to maintain original functionality.

.. warning::
    This feature must be enabled at the start of the project and before initial app migration due to a limitation in Django's swappable API --
    `Read more <https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#changing-to-a-custom-user-model-mid-project>`_

.. tip::
    It is recommended to configure and setup all Salesman models as swappable even if it's not neccesary at the begining.
    This will future proof your application in case you wish to add it later.

.. note::
    For this example, we assume your custom app is named ``shop``.

Create models
=============

First you need to define your models. Make sure to inherit from the Base original model.
To swap all Order models:

.. literalinclude:: /../example/shop/models/order.py

The same can be done for the Basket models as well:

.. literalinclude:: /../example/shop/models/basket.py

Register models
===============

Then register your models in ``settings.py``:

.. code:: python

    SALESMAN_BASKET_MODEL = 'shop.Basket'
    SALESMAN_BASKET_ITEM_MODEL = 'shop.BasketItem'
    SALESMAN_ORDER_MODEL = 'shop.Order'
    SALESMAN_ORDER_ITEM_MODEL = 'shop.OrderItem'
    SALESMAN_ORDER_PAYMENT_MODEL = 'shop.OrderPayment'
    SALESMAN_ORDER_NOTE_MODEL = 'shop.OrderNote'

After that make sure to generate and run the migrations.

.. code:: bash

    python manage.py makemigrations shop
    python manage.py migrate


Referencing models
==================

Instead of referring to Salemsman models directly, you should use the helper function:

.. code:: python

    from salesman.core.utils import get_salesman_model

    BasketItem = get_salesman_model('BasketItem')


**That's it!** You are now the owner of all Salesman models and are free to modify as seen fit.
