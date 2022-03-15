from django.core.exceptions import FieldDoesNotExist
from django.utils.formats import date_format
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from wagtail.admin.edit_handlers import EditHandler

from salesman.conf import app_settings

from ..utils import format_price


class ReadOnlyPanel(EditHandler):
    """
    Read only panel for Wagtail. You can pass in a ``formatter`` function
    to override value format and/or a ``renderer`` function to override how
    the value is rendered in html.
    """

    def __init__(self, attr, *args, **kwargs):
        self.attr = attr
        self.formatter = kwargs.pop('formatter', None)
        self.renderer = kwargs.pop('renderer', None)
        super().__init__(*args, **kwargs)

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs['attr'] = self.attr
        kwargs['formatter'] = self.formatter
        kwargs['renderer'] = self.renderer
        return kwargs

    def on_model_bound(self):
        """
        Set field data from model.
        """
        field, heading = None, ''
        try:
            field = self.model._meta.get_field(self.attr)
            heading = getattr(field, 'verbose_name', '')
        except (FieldDoesNotExist, AttributeError):
            try:
                field = getattr(self.model, self.attr)
                heading = getattr(field, 'short_description', '')
            except AttributeError:
                pass
        if heading and not self.heading:
            self.heading = heading
        if field and not self.help_text:
            self.help_text = getattr(field, 'help_text', '')

    def get_value(self):
        value = getattr(self.instance, self.attr)
        if callable(value):
            value = value(self.instance)
        return value

    def format_value(self, value):
        if self.formatter and value is not None:
            value = self.formatter(value, self.instance, self.request)
        return value

    def render(self):
        value = self.get_value()
        return self.format_value(value)

    def render_as_object(self):
        if self.renderer:
            return self.renderer(self.get_value(), self.instance, self.request)
        return format_html(
            '<fieldset><legend>{}</legend>'
            '<ul class="fields"><li><div class="field">'
            '<div style="padding-top: 1.2em;">{}</div>'
            '</div></li></ul>'
            '</fieldset>',
            self.heading,
            self.render(),
        )

    def render_as_field(self):
        if self.renderer:
            return self.renderer(self.get_value(), self.instance, self.request)
        help_html = (
            format_html('<p class="help">{}</p>', self.help_text)
            if self.help_text
            else ""
        )
        return format_html(
            '<div class="field">'
            '<label>{}{}</label>'
            '<div class="field-content">'
            '<div style="padding-top: 1.2em;">{}</div>{}'
            '</div>'
            '</div>',
            self.heading,
            _(":"),
            self.render(),
            help_html,
        )


class OrderDatePanel(ReadOnlyPanel):
    def format_value(self, value):
        if value:
            value = date_format(value, format='DATETIME_FORMAT')
        return value


class OrderCheckboxPanel(ReadOnlyPanel):
    def format_value(self, value):
        icon, color = ('tick', '#157b57') if value else ('cross', '#cd3238')
        template = '<span class="icon icon-{}" style="color: {};"></span>'
        return format_html(template, icon, color)


class OrderItemsPanel(ReadOnlyPanel):
    def classes(self):
        return ['salesman-order-items']

    def render_as_field(self):
        return self.render()

    def render_as_object(self):
        return self.render()

    def format_json(self, value, obj, request):
        return app_settings.SALESMAN_ADMIN_JSON_FORMATTER(
            value, context={'order_item': True}
        )

    def render(self):
        head = f'''<tr>
            <td>{_('Name')}</td>
            <td>{_('Code')}</td>
            <td>{_('Unit price')}</td>
            <td>{_('Quantity')}</td>
            <td>{_('Subtotal')}</td>
            <td>{_('Extra rows')}</td>
            <td>{_('Total')}</td>
            <td>{_('Extra')}</td>
            </tr>'''

        body = ''
        for item in self.instance.items.all():
            body += f'''<tr>
            <td class="title"><h2>{item.name}</h2></td>
            <td>{item.code}</td>
            <td>{format_price(item.unit_price, self.instance, self.request)}</td>
            <td>{item.quantity}</td>
            <td>{format_price(item.subtotal, self.instance, self.request)}</td>
            <td>{self.format_json(item.extra_rows, self.instance, self.request)}</td>
            <td>{format_price(item.total, self.instance, self.request)}</td>
            <td>{self.format_json(item.extra, self.instance, self.request)}</td>
            </tr>'''

        return format_html(
            '<table class="listing full-width">'
            '<thead>{}</thead>'
            '<tbody>{}</tbody>'
            '</table>',
            mark_safe(head),
            mark_safe(body),
        )


class OrderAdminPanel(ReadOnlyPanel):
    """
    Retrieves value from model_admin which is bound to the form in `get_edit_handler`.
    """

    def on_model_bound(self):
        pass

    def on_form_bound(self):
        if not hasattr(self.form, 'model_admin'):
            raise AssertionError("OrderAdminPanel can only be used in OrderModelAdmin.")

        field = getattr(self.form.model_admin, self.attr)
        heading = getattr(field, 'short_description', '')
        if heading and not self.heading:
            self.heading = heading

    def get_value(self):
        return getattr(self.form.model_admin, self.attr)(self.instance)
