.. _address-validation:

##################
Address validation
##################

During the checkout process, both the *shipping* and *billing* addresses can be specified.
The default address validator is set to :func:`salesman.checkout.utils.validate_address`
that simply makes both address fields required to be entered by the customer.

This behavior can be overridden by providing a dotted path in ``SALESMAN_ADDRESS_VALIDATOR``
setting that points to your custom validator function.

.. tip::

    To validate a specific address format split the text by ``\n`` character and validate each line.

.. code:: python

    def validate_address(value: str, context: dict = {}) -> str:
        """
        Default address validator function. Can be overriden by providing a
        dotted path to a function in ``SALESMAN_ADDRESS_VALIDATOR`` setting.

        Args:
            value (str): Address text to be validated
            context (dict, optional): Validator context data. Defaults to {}.

        Raises:
            ValidationError: In case address is not valid

        Returns:
            str: Validated value
        """
        if not value:
            raise ValidationError(_(f"Address is required."))
        return value

Your custom validator should accept a text ``value`` and return the validated version.
It also receives a ``context`` dictionary with additional context data like ``request``,
a ``basket`` object and ``address`` type (set to either *shipping* or *billing*).
