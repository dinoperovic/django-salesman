.. _api-basket:

######
Basket
######

Api docs for Basket.

.. http:get:: /basket/

    Get basket.

    .. sourcecode:: json

        {
            "id": 1,
            "items": [],
            "subtotal": "0.00",
            "total": "0.00",
            "extra": {},
            "extra_rows": []
        }

.. http:post:: /basket/

    Add an item to the basket. To add the same product with a different configuration to the basket
    you can send a custom ``ref`` parameter. Otherwise a default one is auto-generated.

    :query str basket: pass in ``?basket`` to return an updated basket after the operation.
    :jsonparam str ref: unique item reference, default is slugified ``product_type-product_id``
    :jsonparam str product_type: type formated as ``app_name.Model``
    :jsonparam int product_id: instance id
    :jsonparam int quantity: item quantity, default is 1
    :jsonparam json extra: extra data for basket item, optional
    :statuscode 400: if supplied params are invalid

.. http:delete:: /basket/

    Delete basket.

    :query str basket: pass in ``?basket`` to return an updated basket after the operation.
    :statuscode 204: if deleted

.. http:get:: /basket/count/

    Show basket item count.

    .. sourcecode:: json

        {
            "count": 3
        }

.. http:get:: /basket/quantity/

    Show basket total quantity.

    .. sourcecode:: json

        {
            "quantity": 9
        }

.. http:post:: /basket/clear/

    Clear all items from basket.

    :query str basket: pass in ``?basket`` to return an updated basket after the operation.

.. http:get:: /basket/extra/

    Get basket extra data.

    .. sourcecode:: json

        {
            "extra": {}
        }

.. http:put:: /basket/extra/

    Update basket extra data.

    :query str basket: pass in ``?basket`` to return an updated basket after the operation.
    :jsonparam json extra: update item extra, null values are removed
    :statuscode 400: if supplied params are invalid

.. http:get:: /basket/(str:ref)/

    Get basket item.

    :param str ref: basket item ref

    .. sourcecode:: json

        {
            "url": "http://localhost:8000/api/basket/shopproduct-1/",
            "ref": "shopproduct-1",
            "product_type": "shop.Product",
            "product_id": 1,
            "product": {
                "name": "Product",
                "code": "1"
            },
            "unit_price": "33.00",
            "quantity": 1,
            "subtotal": "33.00",
            "extra_rows": [],
            "total": "33.00",
            "extra": {}
        }

.. http:put:: /basket/(str:ref)/

    Update basket item.

    :param str ref: basket item ref
    :query str basket: pass in ``?basket`` to return an updated basket after the operation.
    :jsonparam int quantity: update item quantity
    :jsonparam json extra: update item extra, null values are removed
    :statuscode 400: if supplied params are invalid

.. http:delete:: /basket/(str:ref)/

    Remove item from basket.

    :param str ref: basket item id
    :query str basket: pass in ``?basket`` to return an updated basket after the operation.
    :statuscode 204: if deleted
