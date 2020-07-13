##########
Unreleased
##########

*TBA*

Added
-----

- Added the ability to display the Basket after other API operations by appending ``?basket`` to url.
- Added the ability to specify a custom validator for ``extra`` field on basket and basket item.
- Added the ability to set ``extra`` data directly in :http:post:`/checkout/` request.

Changed
-------

- Make basket merge a transaction.
- When saving order in wagtail, stay on the order edit page.
- Method ``OrderStatus.validate_transition()`` now returns the validated status as string.

Fixed
-----

- Fixed return type for ``OrderStatus.get_transitions()``.
