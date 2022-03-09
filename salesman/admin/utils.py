import json
from decimal import Decimal

from django.conf import settings
from django.http import HttpRequest
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from rest_framework.compat import pygments_css, pygments_highlight

from salesman.conf import app_settings
from salesman.orders.models import Order


def format_json(value: dict, context: dict = {}) -> str:
    """
    Format json and add color using pygments with fallback.

    Args:
        value (dict): Dict to be formated to json
        context (dict, optional): Format context data. Defaults to {}.

    Returns:
        str: JSON formated html string
    """
    output = json.dumps(value, indent=2)
    output = pygments_highlight(output, 'json', 'tango')
    style = pygments_css('tango')
    styled = context.get('styled', True)  # Used for testing.
    if styled and style:
        html = (
            f'<style>{style}</style>'
            f'<pre class="highlight" style="margin: 0; padding: 1em;">{output}</pre>'
        )
    else:
        html = f'<pre style="margin: 0;">{output}</pre>'
    return format_html('<div>{}</div>', mark_safe(html))


def format_price(value: Decimal, order: Order, request: HttpRequest) -> str:
    """
    Wrapper for format price function with order admin context added.

    Args:
        value (Decimal): Number value to be formatted
        order (Order): Order instance
        request (HttpRequest): Django request

    Returns:
        str: Formatted price as a string
    """
    context = {
        'request': request,
        'order': order,
        'admin': True,
    }
    return app_settings.SALESMAN_PRICE_FORMATTER(value, context=context)


def format_customer(user: settings.AUTH_USER_MODEL, context: dict = {}) -> str:
    """
    Format the customer display in admin orders.

    Args:
        user (User): Order user.
        context (dict, optional): Format context data. Defaults to {}.

    Returns:
        str: Formatted customer display as string
    """
    if context.get("wagtail", False):
        url_name = 'wagtailusers_users:edit'
    else:
        url_name = 'admin:auth_user_change'

    try:
        url = reverse(url_name, args=[user.pk])
        return mark_safe(f'<a href="{url}">{user}</a>')
    except NoReverseMatch:  # pragma: no cover
        return str(user)
