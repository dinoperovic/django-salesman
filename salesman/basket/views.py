from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponseBase
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from salesman.basket.models import BaseBasket, BaseBasketItem
from salesman.core.utils import get_salesman_model

from .serializers import (
    BasketExtraSerializer,
    BasketItemCreateSerializer,
    BasketItemSerializer,
    BasketSerializer,
)

Basket = get_salesman_model("Basket")


class BasketViewSet(viewsets.ModelViewSet):
    """
    Basket API endpoint.
    """

    serializer_class = BasketItemSerializer
    lookup_field = "ref"

    _basket: BaseBasket | None = None

    def get_view_name(self) -> str:
        name = super().get_view_name()
        if name == "Basket List":
            return "Basket"
        if name == "Basket Instance":
            return "Basket Item"
        return name

    def get_basket(self) -> BaseBasket:
        if self._basket:
            return self._basket
        basket: BaseBasket
        basket, _ = Basket.objects.get_or_create_from_request(self.request)
        self._basket = basket
        return basket

    def get_queryset(self) -> QuerySet[BaseBasketItem]:
        return self.get_basket().items.all()

    def get_serializer_class(self) -> type[BaseSerializer]:
        if self.action == "create":
            return BasketItemCreateSerializer
        return super().get_serializer_class()

    def get_serializer_context(self) -> dict[str, Any]:
        context = super().get_serializer_context()
        context["basket"] = self.get_basket()
        return context

    def get_basket_response(self) -> Response:
        context = self.get_serializer_context()
        serializer = BasketSerializer(self.get_basket(), context=context)
        return Response(dict(serializer.data))

    def finalize_response(
        self,
        request: Request,
        response: Response,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """
        Patch response to render the Basket when `?basket` is present in the url.
        """
        if (
            request.method != "GET"
            and "basket" in request.GET
            and status.is_success(response.status_code)
        ):
            response = self.get_basket_response()
        return super().finalize_response(request, response, *args, **kwargs)

    @method_decorator(never_cache)
    def dispatch(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponseBase:
        return super().dispatch(request, *args, **kwargs)

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Show basket and items.
        """
        return self.get_basket_response()

    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Delete the basket.
        """
        self.get_basket().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def count(self, request: Request) -> Response:
        """
        Show basket item count.
        """
        return Response({"count": self.get_basket().count})

    @action(detail=False, methods=["get"])
    def quantity(self, request: Request) -> Response:
        """
        Show basket total quantity.
        """
        return Response({"quantity": self.get_basket().quantity})

    @action(detail=False, methods=["post"], serializer_class=BasketSerializer)
    def clear(self, request: Request) -> Response:
        """
        Clear all items from basket.
        """
        self.get_basket().clear()
        return self.list(request)

    @action(
        detail=False,
        methods=["get", "put"],
        serializer_class=BasketExtraSerializer,
    )
    def extra(self, request: Request) -> Response:
        """
        Update basket extra data.
        """
        basket = self.get_basket()

        if request.method == "GET":
            serializer = self.get_serializer(basket)
            return Response(serializer.data)

        serializer = self.get_serializer(basket, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
