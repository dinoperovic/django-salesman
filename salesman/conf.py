"""
Settings module.
"""


class DefaultSettings:
    def _setting(self, name, default=None):
        from django.conf import settings

        return getattr(settings, name, default)

    def _error(self, message):
        from django.core.exceptions import ImproperlyConfigured

        raise ImproperlyConfigured(message)

    @property
    def SALESMAN_PRODUCT_TYPES(self) -> dict:
        """
        A dictionary of product types and their respected serializers
        that are availible for purchase as product. Should be
        formated as ``'app_label.Model': 'path.to.Serializer'``.
        """
        from django.apps import apps
        from django.utils.module_loading import import_string

        product_types = self._setting('SALESMAN_PRODUCT_TYPES', {})
        ret = {}
        for key, value in product_types.items():
            try:
                app_label, model_name = key.split('.')
            except ValueError:
                self._error(f"Invalid Key `{key}`, format as `app_label.Model`.")
            try:
                model = apps.get_model(app_label, model_name)
                if value:
                    ret[key] = import_string(value)
            except (LookupError, ImportError) as e:
                self._error(e)
            for attr in ['name', 'code']:
                if not hasattr(model, attr):
                    self._error(f"Product type `{key}` must define `{attr}` attribute.")
            if not hasattr(model, 'get_price'):
                self._error(f"Product type `{key}` must implement `get_price` method.")
        return ret

    @property
    def SALESMAN_BASKET_MODIFIERS(self) -> list:
        """
        A list of strings formated as ``path.to.CustomModifier``.
        Modifiers must extend ``salesman.basket.modifiers.BasketModifier`` class.
        and define a unique ``identifier`` attribute.
        """
        from django.utils.module_loading import import_string
        from salesman.basket.modifiers import BasketModifier

        basket_modifiers = self._setting('SALESMAN_BASKET_MODIFIERS', [])
        ret, identifiers = [], []
        for value in basket_modifiers:
            try:
                modifier = import_string(value)
            except ImportError as e:
                self._error(e)
            if not issubclass(modifier, BasketModifier):
                self._error(f"Modifer `{modifier}` must subclass `{BasketModifier}`.")
            identifier = getattr(modifier, 'identifier', None)
            if not identifier:
                self._error(f"Modifier `{modifier}` must define a unique `idetifier`.")
            if identifier in identifiers:
                self._error(f"Modifier `{identifier}` appears more than once.")
            identifiers.append(identifier)
            ret.append(modifier)
        return ret

    @property
    def SALESMAN_PAYMENT_METHODS(self) -> list:
        """
        A list of strings formated as ``path.to.CustomPayment``.
        Payments must extend ``salesman.checkout.payment.PaymentMethod`` class
        and define a unique ``identifier`` attribute.
        """
        from django.utils.module_loading import import_string
        from salesman.checkout.payment import PaymentMethod

        payment_methods = self._setting('SALESMAN_PAYMENT_METHODS', [])
        ret, identifiers = [], []
        for value in payment_methods:
            try:
                payment = import_string(value)
            except ImportError as e:
                self._error(e)
            if not issubclass(payment, PaymentMethod):
                self._error(f"Payment `{payment}` must subclass `{PaymentMethod}`.")
            if not getattr(payment, 'label', None):
                self._error(f"Payment `{payment}` must define a `label`.")
            identifier = getattr(payment, 'identifier', None)
            if not identifier:
                self._error(f"Payment `{payment}` must define a unique `identifier`.")
            if identifier in identifiers:
                self._error(f"Payment `{identifier}` appears more than once.")
            identifiers.append(identifier)
            ret.append(payment)
        return ret

    @property
    def SALESMAN_ADDRESS_VALIDATOR(self) -> callable:
        """
        A dotted path to address validator function. Function should accept a string
        value and return a validated version. Also recieves a ``context`` dictionary
        with additional validator context data like ``request``, a ``basket`` object
        and ``address`` type (set to either *shipping* or *billing*).
        """
        from django.utils.module_loading import import_string

        value = self._setting(
            'SALESMAN_ADDRESS_VALIDATOR', 'salesman.checkout.utils.validate_address'
        )
        try:
            validator = import_string(value)
        except ImportError as e:
            self._error(e)
        if not callable(validator):
            self._error(f"Specified address validator `{validator}` is not callable.")
        return validator

    @property
    def SALESMAN_ORDER_STATUS(self) -> type:
        """
        A dotted path to enum class that contains available order statuses.
        Overriden class must extend ``salesman.orders.status.BaseOrderStatus`` class.
        Can optionally override a class method ``get_payable`` that returns a list of
        statuses an order is eligible to be paid from, ``get_transitions`` method that
        returns a dict of statuses with their transitions and ``validate_transition``
        method to validate status transitions.
        """
        from django.utils.module_loading import import_string
        from salesman.orders.status import BaseOrderStatus

        value = self._setting(
            'SALESMAN_ORDER_STATUS', 'salesman.orders.status.OrderStatus'
        )
        try:
            status = import_string(value)
        except ImportError as e:
            self._error(e)
        if not issubclass(status, BaseOrderStatus):
            self._error(f"Status `{status}` must subclass `{BaseOrderStatus}`.")
        required = ['NEW', 'CREATED', 'COMPLETED', 'REFUNDED']
        for item in required:
            if item not in status.names or status[item].value != item:
                self._error(
                    "Status must specify members with names/values "
                    "`NEW`, `CREATED`, `COMPLETED` and `REFUNDED`."
                )
        return status

    @property
    def SALESMAN_ORDER_REFERENCE_GENERATOR(self) -> callable:
        """
        A dotted path to reference generator function for new orders.
        Function should accept a django request object as param: ``request``.
        Value returned from the function will be slugified.
        """
        from django.utils.module_loading import import_string

        value = self._setting(
            'SALESMAN_ORDER_REFERENCE_GENERATOR', 'salesman.orders.utils.generate_ref',
        )
        try:
            generator = import_string(value)
        except ImportError as e:
            self._error(e)
        if not callable(generator):
            self._error(f"Specified reference generator `{generator}` is not callable.")
        return generator

    @property
    def SALESMAN_PRICE_FORMATTER(self) -> callable:
        """
        A dotted path to price formatter function. Function should accept a value
        of type: ``Decimal`` and return a price formatted string. Also recieves
        a ``context`` dictionary with additional render data like ``request``
        and either the ``basket`` or ``order`` object.
        """
        from django.utils.module_loading import import_string

        value = self._setting(
            'SALESMAN_PRICE_FORMATTER', 'salesman.core.utils.format_price'
        )
        try:
            formatter = import_string(value)
        except ImportError as e:
            self._error(e)
        if not callable(formatter):
            self._error(f"Specified price formatter `{formatter}` is not callable.")
        return formatter

    @property
    def SALESMAN_ADMIN_REGISTER(self) -> bool:
        """
        Set to ``False`` to skip Salesman admin registration, in case
        you wish to build your own ``ModelAdmin`` for Django or Wagtail.
        """
        return self._setting('SALESMAN_ADMIN_REGISTER', True)


app_settings = DefaultSettings()
