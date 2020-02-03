.. _reference-admin:

#####
Admin
#####

Admin reference.

Utils
=====

.. autofunction:: salesman.admin.utils.format_json
.. autofunction:: salesman.admin.utils.format_price

Widgets
=======

.. autoclass:: salesman.admin.widgets.OrderStatusSelect
.. autoclass:: salesman.admin.widgets.PaymentSelect

Admin
=====

.. autoclass:: salesman.admin.admin.OrderItemInline
.. autoclass:: salesman.admin.admin.OrderPaymentModelForm
.. autoclass:: salesman.admin.admin.OrderPaymentInline
.. autoclass:: salesman.admin.admin.OrderModelForm
.. autoclass:: salesman.admin.admin.OrderStatusFilter
.. autoclass:: salesman.admin.admin.BaseOrderAdmin
.. autoclass:: salesman.admin.admin.OrderRefundMixin
.. autoclass:: salesman.admin.admin.OrderAdmin
    :show-inheritance:


Edit handlers
=============

.. autoclass:: salesman.admin.edit_handlers.ReadOnlyPanel

Wagtail hooks
=============

.. autofunction:: salesman.admin.wagtail_hooks._format_json
.. autofunction:: salesman.admin.wagtail_hooks._format_date
.. autofunction:: salesman.admin.wagtail_hooks._format_is_paid
.. autofunction:: salesman.admin.wagtail_hooks._render_items
.. autoclass:: salesman.admin.wagtail_hooks.OrderIndexView
.. autoclass:: salesman.admin.wagtail_hooks.OrderEditView
.. autoclass:: salesman.admin.wagtail_hooks.OrderPermissionHelper
.. autoclass:: salesman.admin.wagtail_hooks.OrderButtonHelper
.. autoclass:: salesman.admin.wagtail_hooks.BaseOrderAdmin
.. autoclass:: salesman.admin.wagtail_hooks.OrderRefundView
.. autoclass:: salesman.admin.wagtail_hooks.OrderRefundMixin
.. autoclass:: salesman.admin.wagtail_hooks.OrderAdmin
    :show-inheritance:
