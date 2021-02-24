##########
Unreleased
##########

*TBA*

Added
-----

- Add support for ``Wagtail 2.12``.
- Optimize basket by prefetching the related products in ``get_items``.
- Added an option to customize Customer formatting in admin, see: :ref:`admin-customer-formatter`.

Fixed
-----

- Allow ``OrderViewSet`` to be called without a ``lookup_field`` to fix schema generation.
- Ensure that ``ProductField`` has ``request`` available through context.
