# Saleman's Example

This example project is used for testing of *Salesman*. You can use it to kickstart your project and get a feel for what's available in the package.

## Installation

Salesman uses [Poetry](https://python-poetry.org/) for virtualenv and dependency management. Make sure you have it installed first.

### Clone the repo

```bash
git clone https://github.com/dinoperovic/django-salesman.git
```

### Run the example

```bash
cd django-salesman/
poetry install -E example
poetry run example/manage.py migrate
poetry run example/manage.py create_dummy_products
poetry run example/manage.py createsuperuser
poetry run example/manage.py runserver
```

**Done!** You can now:

- Navigate to `/api/` and start adding products to the basket and purchase items.
- View orders in both the regular Django admin (`/admin/`) or [Wagtail](https://wagtail.io) cms (`/cms/`).

## Documentation

Documentation is available on [Read the Docs](https://django-salesman.readthedocs.org).
