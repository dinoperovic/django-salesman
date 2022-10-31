from __future__ import annotations

from typing import Any

from django.core.exceptions import FieldDoesNotExist
from django.http import HttpRequest
from django.utils.formats import date_format
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from wagtail.admin.edit_handlers import EditHandler as Panel
from wagtail.utils.version import get_main_version as get_wagtail_version

from salesman.conf import app_settings

from ..utils import format_price

if get_wagtail_version() < "3.0.0":  # pragma: no cover
    # Attach dummy BoundPanel class for older Wagtail versions
    Panel.BoundPanel = object


class ReadOnlyPanel(Panel):
    """
    Read only panel for Wagtail. You can pass in a ``formatter`` function
    to override value format and/or a ``renderer`` function to override how
    the value is rendered in html.
    """

    def __init__(self, attr: str, *args: Any, **kwargs: Any) -> None:
        self.attr = attr
        self.formatter = kwargs.pop("formatter", None)
        self.renderer = kwargs.pop("renderer", None)
        super().__init__(*args, **kwargs)

    def clone_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = super().clone_kwargs()
        kwargs["attr"] = self.attr
        kwargs["formatter"] = self.formatter
        kwargs["renderer"] = self.renderer
        return kwargs

    def on_model_bound(self) -> None:
        """
        Set field data from model.
        """
        field, heading = None, ""
        try:
            field = self.model._meta.get_field(self.attr)
            heading = getattr(field, "verbose_name", "")
        except (FieldDoesNotExist, AttributeError):
            try:
                field = getattr(self.model, self.attr)
                heading = getattr(field, "short_description", "")
            except AttributeError:
                pass
        if heading and not self.heading:
            self.heading: str = heading
        if field and not self.help_text:
            self.help_text: str = getattr(field, "help_text", "")

    def get_value(self) -> Any:  # pragma: no cover
        value = getattr(self.instance, self.attr)
        if callable(value):
            value = value(self.instance)
        return value

    def format_value(self, value: Any) -> Any:  # pragma: no cover
        if self.formatter and value is not None:
            value = self.formatter(value, self.instance, self.request)
        return value

    def render(self) -> Any:  # pragma: no cover
        value = self.get_value()
        return self.format_value(value)

    def render_as_object(self) -> Any:  # pragma: no cover
        if self.renderer:
            return self.renderer(self.get_value(), self.instance, self.request)
        return format_html(
            "<fieldset><legend>{}</legend>"
            '<ul class="fields"><li><div class="field">'
            '<div style="padding-top: 1.2em;">{}</div>'
            "</div></li></ul>"
            "</fieldset>",
            self.heading,
            self.render(),
        )

    def render_as_field(self) -> Any:  # pragma: no cover
        if self.renderer:
            return self.renderer(self.get_value(), self.instance, self.request)
        help_html = (
            format_html('<p class="help">{}</p>', self.help_text)
            if self.help_text
            else ""
        )
        return format_html(
            '<div class="field">'
            "<label>{}{}</label>"
            '<div class="field-content">'
            '<div style="padding-top: 1.2em;">{}</div>{}'
            "</div>"
            "</div>",
            self.heading,
            _(":"),
            self.render(),
            help_html,
        )

    class BoundPanel(Panel.BoundPanel):
        heading: str
        help_text: str

        def __init__(
            self,
            panel: Panel,
            **kwargs: Any,
        ) -> None:
            super().__init__(panel, **kwargs)
            self.attr = panel.attr
            self.formatter = panel.formatter
            self.renderer = panel.renderer

        def get_value(self) -> Any:
            value = getattr(self.instance, self.attr)
            if callable(value):
                value = value(self.instance)
            return value

        def format_value(self, value: Any) -> Any:
            if self.formatter and value is not None:
                value = self.formatter(value, self.instance, self.request)
            return value

        def render(self) -> Any:
            value = self.get_value()
            return self.format_value(value)

        def render_html(self, context: dict[str, Any]) -> Any:
            """
            New method for rendering the field in Wagtail 4.
            """
            if self.renderer:
                return self.renderer(self.get_value(), self.instance, self.request)
            return format_html(
                "<div>{}</div>",
                self.render(),
            )

        def render_as_object(self) -> Any:
            if self.renderer:
                return self.renderer(self.get_value(), self.instance, self.request)
            return format_html(
                "<fieldset><legend>{}</legend>"
                '<ul class="fields"><li><div class="field">'
                '<div style="padding-top: 1.2em;">{}</div>'
                "</div></li></ul>"
                "</fieldset>",
                self.heading,
                self.render(),
            )

        def render_as_field(self) -> Any:
            if self.renderer:
                return self.renderer(self.get_value(), self.instance, self.request)
            help_html = (
                format_html('<p class="help">{}</p>', self.help_text)
                if self.help_text
                else ""
            )
            return format_html(
                '<div class="field">'
                "<label>{}{}</label>"
                '<div class="field-content">'
                '<div style="padding-top: 1.2em;">{}</div>{}'
                "</div>"
                "</div>",
                self.heading,
                _(":"),
                self.render(),
                help_html,
            )


class OrderDatePanel(ReadOnlyPanel):
    def format_value(self, value: Any) -> Any:  # pragma: no cover
        if value:
            value = date_format(value, format="DATETIME_FORMAT")
        return value

    class BoundPanel(ReadOnlyPanel.BoundPanel):
        def format_value(self, value: Any) -> Any:
            if value:
                value = date_format(value, format="DATETIME_FORMAT")
            return value


class OrderCheckboxPanel(ReadOnlyPanel):
    def format_value(self, value: Any) -> str:  # pragma: no cover
        icon, color = ("tick", "#157b57") if value else ("cross", "#cd3238")
        template = '<span class="icon icon-{}" style="color: {};"></span>'
        return format_html(template, icon, color)

    class BoundPanel(ReadOnlyPanel.BoundPanel):
        def format_value(self, value: Any) -> str:
            icon, color = ("tick", "#157b57") if value else ("cross", "#cd3238")
            template = '<span class="icon icon-{}" style="color: {};"></span>'
            return format_html(template, icon, color)


class OrderItemsPanel(ReadOnlyPanel):
    def classes(self) -> list[str]:  # pragma: no cover
        return ["salesman-order-items"]

    def render_as_field(self) -> str:  # pragma: no cover
        return self.render()

    def render_as_object(self) -> str:  # pragma: no cover
        return self.render()

    def format_json(
        self,
        value: dict[str, Any],
        obj: Any,
        request: HttpRequest,
    ) -> str:  # pragma: no cover
        return app_settings.SALESMAN_ADMIN_JSON_FORMATTER(
            value, context={"order_item": True}
        )

    def render(self) -> str:  # pragma: no cover
        head = f"""<tr>
            <td>{_('Name')}</td>
            <td>{_('Code')}</td>
            <td>{_('Unit price')}</td>
            <td>{_('Quantity')}</td>
            <td>{_('Subtotal')}</td>
            <td>{_('Extra rows')}</td>
            <td>{_('Total')}</td>
            <td>{_('Extra')}</td>
            </tr>"""

        body = ""
        for item in self.instance.items.all():
            body += f"""<tr>
            <td class="title"><h2>{item.name}</h2></td>
            <td>{item.code}</td>
            <td>{format_price(item.unit_price, self.instance, self.request)}</td>
            <td>{item.quantity}</td>
            <td>{format_price(item.subtotal, self.instance, self.request)}</td>
            <td>{self.format_json(item.extra_rows, self.instance, self.request)}</td>
            <td>{format_price(item.total, self.instance, self.request)}</td>
            <td>{self.format_json(item.extra, self.instance, self.request)}</td>
            </tr>"""

        return format_html(
            '<table class="listing full-width">'
            "<thead>{}</thead>"
            "<tbody>{}</tbody>"
            "</table>",
            mark_safe(head),
            mark_safe(body),
        )

    class BoundPanel(ReadOnlyPanel.BoundPanel):
        def classes(self) -> list[str]:
            return ["salesman-order-items"]

        def render_as_field(self) -> str:
            return self.render()

        def render_as_object(self) -> str:
            return self.render()

        def format_json(
            self, value: dict[str, Any], obj: Any, request: HttpRequest
        ) -> str:
            return app_settings.SALESMAN_ADMIN_JSON_FORMATTER(
                value, context={"order_item": True}
            )

        def render(self) -> str:
            head = f"""<tr>
                <td>{_('Name')}</td>
                <td>{_('Code')}</td>
                <td>{_('Unit price')}</td>
                <td>{_('Quantity')}</td>
                <td>{_('Subtotal')}</td>
                <td>{_('Extra rows')}</td>
                <td>{_('Total')}</td>
                <td>{_('Extra')}</td>
                </tr>"""

            body = ""
            for item in self.instance.items.all():
                body += f"""<tr>
                <td class="title"><h2>{item.name}</h2></td>
                <td>{item.code}</td>
                <td>{format_price(item.unit_price, self.instance, self.request)}</td>
                <td>{item.quantity}</td>
                <td>{format_price(item.subtotal, self.instance, self.request)}</td>
                <td>{self.format_json(item.extra_rows, self.instance, self.request)}</td>
                <td>{format_price(item.total, self.instance, self.request)}</td>
                <td>{self.format_json(item.extra, self.instance, self.request)}</td>
                </tr>"""  # noqa

            return format_html(
                '<table class="listing full-width">'
                "<thead>{}</thead>"
                "<tbody>{}</tbody>"
                "</table>",
                mark_safe(head),
                mark_safe(body),
            )


class OrderAdminPanel(ReadOnlyPanel):
    """
    Retrieves value from model_admin which is bound to the form in `get_edit_handler`.
    """

    def on_model_bound(self) -> None:
        pass

    def on_form_bound(self) -> None:  # pragma: no cover
        if not hasattr(self.form, "model_admin"):
            raise AssertionError("OrderAdminPanel can only be used in OrderModelAdmin.")

        field = getattr(self.form.model_admin, self.attr)
        heading = getattr(field, "short_description", "")
        if heading and not self.heading:
            self.heading = heading

    def get_value(self) -> Any:  # pragma: no cover
        return getattr(self.form.model_admin, self.attr)(self.instance)

    class BoundPanel(ReadOnlyPanel.BoundPanel):
        def __init__(
            self,
            panel: Panel,
            **kwargs: Any,
        ) -> None:
            super().__init__(panel, **kwargs)

            if not hasattr(self.form, "model_admin"):
                raise AssertionError(
                    "OrderAdminPanel can only be used in OrderModelAdmin."
                )

            field = getattr(self.form.model_admin, self.attr)
            heading = getattr(field, "short_description", "")
            if heading and not self.heading:
                self.heading = heading

        def get_value(self) -> Any:
            return getattr(self.form.model_admin, self.attr)(self.instance)
