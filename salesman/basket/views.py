from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from salesman.core.utils import get_salesman_model

from .serializers import (
    BasketExtraSerializer,
    BasketItemCreateSerializer,
    BasketItemSerializer,
    BasketSerializer,
)

Basket = get_salesman_model('Basket')


class BasketViewSet(viewsets.ModelViewSet):
    """
    Basket API endpoint.
    """

    serializer_class = BasketItemSerializer
    lookup_field = 'ref'

    _basket = None

    def get_view_name(self):
        name = super().get_view_name()
        if name == "Basket List":
            return "Basket"
        if name == "Basket Instance":
            return "Basket Item"
        return name

    def get_basket(self):
        if not self._basket:
            self._basket, _ = Basket.objects.get_or_create_from_request(self.request)
        return self._basket

    def get_queryset(self):
        return self.get_basket().items.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return BasketItemCreateSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['basket'] = self.get_basket()
        return context

    def get_basket_response(self):
        context = self.get_serializer_context()
        serializer = BasketSerializer(self.get_basket(), context=context)
        return Response(dict(serializer.data))

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Patch response to render the Basket when `?basket` is present in the url.
        """
        if (
            request.method != 'GET'
            and 'basket' in request.GET
            and status.is_success(response.status_code)
        ):
            response = self.get_basket_response()
        return super().finalize_response(request, response, *args, **kwargs)

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Show basket and items.
        """
        return self.get_basket_response()

    def delete(self, request, *args, **kwargs):
        """
        Delete the basket.
        """
        self.get_basket().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def count(self, request):
        """
        Show basket item count.
        """
        return Response({'count': self.get_basket().count})

    @action(detail=False, methods=['get'])
    def quantity(self, request):
        """
        Show basket total quantity.
        """
        return Response({'quantity': self.get_basket().quantity})

    @action(detail=False, methods=['post'], serializer_class=BasketSerializer)
    def clear(self, request):
        """
        Clear all items from basket.
        """
        self.get_basket().clear()
        return self.list(request)

    @action(
        detail=False, methods=['get', 'put'], serializer_class=BasketExtraSerializer
    )
    def extra(self, request):
        """
        Update basket extra data.
        """
        basket = self.get_basket()

        if request.method == 'GET':
            serializer = self.get_serializer(basket)
            return Response(serializer.data)

        serializer = self.get_serializer(basket, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
