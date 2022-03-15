from django.utils.translation import gettext_lazy as _
from wagtail.contrib.modeladmin.helpers import (
    AdminURLHelper,
    ButtonHelper,
    PermissionHelper,
)


class OrderPermissionHelper(PermissionHelper):
    def user_can_create(self, user):
        return False

    def user_can_delete_obj(self, user, obj):
        return False


class OrderButtonHelper(ButtonHelper):
    def edit_button(self, *args, **kwargs):
        button = super().edit_button(*args, **kwargs)
        button.update({'label': _("View"), 'title': _("View this Order")})
        return button


class OrderAdminURLHelper(AdminURLHelper):
    pass
