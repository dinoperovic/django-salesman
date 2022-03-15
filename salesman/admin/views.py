from django.shortcuts import redirect
from django.urls import NoReverseMatch
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin import messages
from wagtail.contrib.modeladmin.views import DeleteView, EditView, IndexView


class OrderIndexView(IndexView):
    """
    Wagtail admin view that handles Order index.
    """

    def dispatch(self, request, *args, **kwargs):
        self.model.request = request
        return super().dispatch(request, *args, **kwargs)


class OrderEditView(EditView):
    """
    Wagtail admin view that handles Order edit.
    """

    page_title = _('Order')

    def dispatch(self, request, *args, **kwargs):
        self.model.request = request
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.edit_url

    def get_meta_title(self):
        return _('Viewing Order')

    @cached_property
    def refund_url(self):
        try:
            return self.url_helper.get_action_url('refund', self.pk_quoted)
        except NoReverseMatch:  # pragma: no cover
            return None


class OrderRefundView(DeleteView):
    """
    Wagtail admin view that handles Order refunds.
    """

    page_title = _('Refund')

    def check_action_permitted(self, user):
        return True

    def get_meta_title(self):
        return _('Confirm Order refund')

    def post(self, request, *args, **kwargs):
        if '_refund-error' in request.POST:
            # Refund error, add error message and redirect to change view.
            msg = _("There was an error while trying to refund order.")
            messages.error(request, msg)

        if '_refund-success' in request.POST:
            # Refund success, add success message and redirect to change view.
            failed = int(request.POST['_refund-success'])
            if failed:
                msg = _("The Order “{}” was only partially refunded.")
                messages.warning(request, msg.format(self.instance))
            else:
                msg = _("The Order “{}” was successfully refunded.")
                messages.success(request, msg.format(self.instance))

        return redirect(self.edit_url)

    def get_template_names(self):
        return ['salesman/admin/wagtail_refund.html']
