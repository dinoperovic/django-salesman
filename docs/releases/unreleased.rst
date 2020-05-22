##########
Unreleased
##########

*TBA*

Added
-----

- Added the ability to specify a custom validator for ``extra`` field on basket and basket item.
- Added the ability to set ``extra`` data directly in :http:post:`/checkout/` request.

Changed
-------

- Make basket merge a transaction.
- When saving order in wagtail, stay on order edit page.

Fixed
-----

- Fixed return type for ``OrderStatus.get_transitions()``.
