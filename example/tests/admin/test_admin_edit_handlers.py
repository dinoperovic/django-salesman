import pytest

from salesman.admin import utils
from salesman.admin.edit_handlers import ReadOnlyPanel
from salesman.admin.models import Order


@pytest.mark.django_db
def test_read_only_panel():
    order = Order.objects.create(ref="1", subtotal=120, total=120)

    panel = ReadOnlyPanel('status')
    panel.model = Order
    panel.instance = order

    # test clone
    kwargs = panel.clone_kwargs()
    assert 'attr' in kwargs
    assert 'formatter' in kwargs
    assert 'renderer' in kwargs

    # test data from field set
    panel.on_model_bound()
    field = Order._meta.get_field('status')
    assert panel.heading == field.verbose_name
    assert panel.help_text == field.help_text

    # test render with formatter
    assert panel.render() == 'NEW'

    def _formatter(value, obj, request):
        return "<span>NEW</span>"

    panel.formatter = _formatter
    assert panel.render() == "<span>NEW</span>"

    # test render as with renderer
    assert panel.render_as_object().startswith('<fieldset><legend>Status</legend>')
    result = '<div class="field"><label>Status:</label>'
    assert panel.render_as_field().startswith(result)

    def _renderer(value, obj, request):
        return "<div>New</div>"

    panel.renderer = _renderer
    assert panel.render_as_object() == "<div>New</div>"
    assert panel.render_as_field() == "<div>New</div>"

    # test callable property
    panel = ReadOnlyPanel('total_display')
    panel.model = Order
    panel.instance = order
    panel.on_model_bound()
    assert panel.heading == Order.total_display.short_description
    assert panel.render() == utils.format_price(120, order=None, request=None)
