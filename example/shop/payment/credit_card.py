# payment.py
import uuid

from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import path, reverse

from salesman.checkout.payment import PaymentMethod
from shop.models import Basket, Order


class CreditCardPayment(PaymentMethod):
    """
    Example payment integration using external service.
    """

    identifier = "credit-card"
    label = "Credit card"

    def get_urls(self):
        """
        Add extra urls for payment that will be included under the defined
        identifier namespace => `/payment/credit-card/return/`.
        """
        return [
            path("purchase/", self.purchase_view, name="credit-card-purchase"),
            path("return/", self.return_view, name="credit-card-return"),
        ]

    def get_redirect_url(self, order, request):
        """
        Return redirect url to external payment gateway or process payment
        using http lib like `requests`. Raise `PaymentError` if issues appear.
        """
        return_url = reverse("credit-card-return")
        purchase_url = reverse("credit-card-purchase")
        url = f"{purchase_url}?ref={order.ref}&return_url={return_url}"
        return request.build_absolute_uri(url)

    def basket_payment(self, basket, request):
        """
        Create order from request without items, store `basket_id` to populate items
        to order once the payment is completed. This is optional in case the payment
        gateway requires a correct order reference (number). You could just as well use
        the basket ID as a reference instead and create an order from basket on success.
        """
        order = Order.objects.create_from_request(request)
        order.extra["basket_id"] = basket.id
        order.save(update_fields=["extra"])
        return self.get_redirect_url(order, request)

    def order_payment(self, order, request):
        """
        Optionally implement this method to enable payment for existing order.
        Remove `basket_id` from order extra since items are already populated.
        """
        order.extra.pop("basket_id", None)
        order.save(update_fields=["extra"])
        return self.get_redirect_url(order, request)

    def refund_payment(self, payment):
        """
        Logic for refunding a given `OrderPayment` instance goes here...
        Return `True` if refund is completed.
        """
        payment.delete()
        return True

    def purchase_view(self, request):
        """
        Dummy external purchase view where customer pays for order.
        """
        try:
            ref = request.GET["ref"]
            return_url = request.GET["return_url"]
        except KeyError:
            return HttpResponse("Invalid request.")

        url = f"{return_url}?ref={ref}&transaction_id={uuid.uuid4()}"
        return HttpResponse(f'<a href="{url}">Purchase</a>')

    def return_view(self, request):
        """
        Return view for credit-card payment, validate the result from request.
        """
        try:
            ref = request.GET["ref"]
            transaction_id = request.GET["transaction_id"]
        except KeyError:
            return HttpResponse("Invalid request")

        try:
            order = Order.objects.get(ref=ref)
            basket_id = order.extra.pop("basket_id", None)
            if basket_id is not None:
                # Populate items from basket.
                basket = Basket.objects.get(id=basket_id)
                order.populate_from_basket(basket, request, status="PROCESSING")
                basket.delete()
            else:
                # Order already populated, change status.
                order.status = "PROCESSING"
                order.save(update_fields=["status"])

            # Store order payment.
            order.pay(
                amount=order.amount_outstanding,
                transaction_id=transaction_id,
                payment_method=self.identifier,
            )

            success_url = reverse("salesman-order-last") + f"?token={order.token}"
            return redirect(request.build_absolute_uri(success_url))
        except (Order.DoesNotExist, Basket.DoesNotExist):
            return HttpResponse("Error capturing payment")
