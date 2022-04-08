from __future__ import annotations

from typing import Any

from django import forms

from salesman.conf import app_settings
from salesman.core.utils import get_salesman_model

from .widgets import OrderStatusSelect, PaymentSelect

Order = get_salesman_model("Order")
OrderPayment = get_salesman_model("OrderPayment")
OrderNote = get_salesman_model("OrderNote")


class OrderModelForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude: list[str] = []
        widgets = {
            "status": OrderStatusSelect,
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if "status" in self.fields:
            self.fields["status"].widget.order = self.instance

    def clean_status(self) -> str:
        status, order = self.cleaned_data["status"], self.instance
        return app_settings.SALESMAN_ORDER_STATUS.validate_transition(status, order)


class OrderPaymentModelForm(forms.ModelForm):
    class Meta:
        model = OrderPayment
        exclude: list[str] = []
        widgets = {
            "payment_method": PaymentSelect,
        }


class OrderNoteModelForm(forms.ModelForm):
    class Meta:
        model = OrderNote
        exclude: list[str] = []
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4, "cols": 60}),
        }
