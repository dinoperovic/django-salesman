.. _installation:

############
Installation
############

A guide on how to install Salesman.

.. raw:: html

    <h3>1. Install using <a href="https://pypi.org/project/pip/">pip</a></h3>

.. code:: bash

    pip install django-salesman

.. note::

    Optionally install the `Pygments <https://pygments.org/>`_ library for a nicer code display in admin.
    You can use the command ``pip install django-salesman[pygments]``

.. raw:: html

    <h3>2. Add to your <code class="literal">settings.py</code></h3>

.. code:: python

    INSTALLED_APPS = [
        ...
        'salesman.core',
        'salesman.basket',
        'salesman.checkout',
        'salesman.orders',
        'salesman.admin',

        'rest_framework',
    ]

.. raw:: html

    <h3>3. Add neccesary urls in <code class="literal">urls.py</code></h3>

.. code:: python

    from django.urls import include, path

    urlpatterns = [
        ...
        path('api/', include('salesman.urls')),
    ]

.. raw:: html

    <h3>4. Run the migrations and start server</h3>

.. code:: bash

    python manage.py migrate
    python manage.py runserver

.. tip::
    It is recommended to configure and setup all Salesman models as swappable even if it's not neccesary at the begining.
    This will future proof your application in case you wish to add it later.
    This has to be done before the initial migrations are created. See :ref:`swappable_models`.

**Done!** Salesman is installed and you can navigate the API by going to ``http://localhost:8000/api/``.
But since no product types are configured there is nothing to be added to the basket yet.
