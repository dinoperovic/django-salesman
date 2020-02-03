from django.core.exceptions import FieldDoesNotExist
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from wagtail.admin.edit_handlers import EditHandler


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
        try:
            field = self.model._meta.get_field(self.attr)
            heading = getattr(field, 'verbose_name', '')
        except FieldDoesNotExist:
            field = getattr(self.model, self.attr)
            heading = getattr(field, 'short_description', '')
        if not self.heading:
            self.heading = heading
        if not self.help_text:
            self.help_text = getattr(field, 'help_text', '')

    def render(self):
        value = getattr(self.instance, self.attr)
        if callable(value):
            value = value()
        if self.formatter and value is not None:
            value = self.formatter(value, self.instance, self.request)
        return value

    def render_as_object(self):
        if self.renderer:
            return self.renderer(self.render(), self.instance, self.request)
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
            return self.renderer(self.render(), self.instance, self.request)
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
