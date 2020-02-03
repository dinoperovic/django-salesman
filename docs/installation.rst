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

    Optionally install `Pygments <https://pygments.org/>`_ library for a nicer code display in admin.

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

    urlpatterns = [
        ...
        path('api/', include('salesman.urls')),
    ]

.. raw:: html

    <h3>4. Run the migrations and start server</h3>

.. code:: bash

    python manage.py migrate
    python manage.py runserver

**Done!** Salesman is installed and you can navigate the API by going to ``http://localhost:8000/api/``.
But since no product types are configured there is nothing to be added to the basket yet.
