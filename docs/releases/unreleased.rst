##########
Unreleased
##########

*TBA*

Added
-----

- Add support for ``Wagtail 2.12``.
- Optimize Basket ``get_items`` by prefetching the related products.

Fixed
-----

- Allow ``OrderViewSet`` to be called without a ``lookup_field`` to fix schema generation.
- Ensure that ``ProductField`` has ``request`` available through context.
