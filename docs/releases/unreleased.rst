##########
Unreleased
##########

*TBA*

Added
-----

- Add support for ``Wagtail 2.12``.
- Optimize basket by prefetching the related products in ``get_items``.

Fixed
-----

- Allow ``OrderViewSet`` to be called without a ``lookup_field`` to fix schema generation.
- Ensure that ``ProductField`` has ``request`` available through context.
