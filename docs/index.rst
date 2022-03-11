########
Salesman
########

.. raw:: html

    <h3>Headless e-commerce framework for Django and Wagtail.</h3>

.. image:: https://img.shields.io/pypi/v/django-salesman
    :target: https://pypi.org/project/django-salesman/
    :alt: PyPI
.. image:: https://img.shields.io/github/workflow/status/dinoperovic/django-salesman/Test/master
    :target: https://github.com/dinoperovic/django-salesman/actions?query=workflow:Test
    :alt: GitHub Workflow Status (branch)
.. image:: https://img.shields.io/codecov/c/github/dinoperovic/django-salesman/master
    :target: http://codecov.io/github/dinoperovic/django-salesman
    :alt: Codecov branch
.. image:: https://img.shields.io/pypi/pyversions/django-salesman
    :target: https://pypi.org/project/django-salesman/
    :alt: PyPI - Python Version
.. image:: https://img.shields.io/pypi/djversions/django-salesman
    :target: https://pypi.org/project/django-salesman/
    :alt: PyPI - Django Version
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code style: black

**Salesman** provides a configurable system for building an online store.
It includes a **RESTful** API with endpoints for manipulating the basket,
processing the checkout and payment operations as well as managing customer orders.

Features
========

- API endpoints for **Basket**, **Checkout** and **Order**
- Support for as many **Product** types needed using generic relations
- Pluggable **Modifier** system for basket processing
- **Payment** methods interface to support any gateway necessary
- Customizable **Order** implementation
- Fully swappable **Order** and **Basket** models
- `Wagtail <https://wagtail.io/>`_ and **Django** admin implementation

.. toctree::
    :caption: Getting Started
    :maxdepth: 1

    installation
    adding_products
    checkout_and_payment

.. toctree::
    :caption: Advanced Usage
    :maxdepth: 1

    advanced/basket_modifiers
    advanced/payment_methods
    advanced/order_customization
    advanced/sending_notifications
    advanced/custom_validators
    advanced/custom_formatters
    advanced/swappable_models

.. toctree::
    :caption: API Documentation
    :maxdepth: 1

    api/basket
    api/checkout
    api/orders

.. toctree::
    :caption: Extras
    :maxdepth: 1

    reference/index
    releases/index
    credits

.. image:: _static/buymeacoffee.svg
    :target: https://www.buymeacoffee.com/dinoperovic
    :alt: Buy me a coffee
