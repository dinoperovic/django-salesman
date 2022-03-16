from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from salesman.checkout.payment import PaymentError, payment_methods_pool
from salesman.conf import app_settings
from salesman.core.utils import get_salesman_model

from .serializers import (
    OrderPaySerializer,
    OrderRefundSerializer,
    OrderStatusSerializer,
)

Order = get_salesman_model('Order')


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Orders API endpoint.
    """

    serializer_class = app_settings.SALESMAN_ORDER_SERIALIZER
    lookup_field = 'ref'

    def get_queryset(self):
        queryset = self.optimize_queryset(Order.objects.all())

        if self.request.user.is_authenticated:
            if self.request.user.is_staff and self.action != 'list':
                # Allow access for admin user to all orders except on `list`.
                return queryset
            return queryset.filter(user=self.request.user.id)

        if 'token' in self.request.GET:
            # Allow non-authenticated users access to order with token.
            return queryset.filter(token=self.request.GET['token'])

        return Order.objects.none()

    def optimize_queryset(self, queryset):
        """
        Extract fields for pre-fetching from order serializer and apply to queryset.
        """
        serializer_class = self.get_serializer_class()
        if hasattr(serializer_class, 'Meta'):
            fields = getattr(serializer_class.Meta, 'select_related_fields', None)
            if fields and (isinstance(fields, list) or isinstance(fields, tuple)):
                queryset = queryset.select_related(*fields)
            fields = getattr(serializer_class.Meta, 'prefetch_related_fields', None)
            if fields and (isinstance(fields, list) or isinstance(fields, tuple)):
                queryset = queryset.prefetch_related(*fields)
        return queryset

    def get_object(self):
        if not hasattr(self, '_object'):
            self._object = super().get_object()
        return self._object

    def get_serializer_class(self):
        if self.action in ['list', 'all']:
            return app_settings.SALESMAN_ORDER_SUMMARY_SERIALIZER
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.detail and self.lookup_field in self.kwargs:
            context['order'] = self.get_object()
        return context

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def last(self, request):
        """
        Show last customer order.
        """
        order = self.get_queryset().order_by('date_created').last()
        if not order:
            raise Http404
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def all(self, request):
        """
        Show all orders to the admin user.
        """
        return self.list(request)

    @action(
        detail=True,
        methods=['get', 'put'],
        serializer_class=OrderStatusSerializer,
        permission_classes=[IsAdminUser],
    )
    def status(self, request, ref):
        """
        Change order status. Available only to admin user.
        """
        order = self.get_object()

        if request.method == 'GET':
            serializer = self.get_serializer(order)
            return Response(serializer.data)

        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'], serializer_class=OrderPaySerializer)
    def pay(self, request, ref):
        """
        Pay for order.
        """
        if request.method == 'GET':
            instance = {'payment_methods': payment_methods_pool.get_payments('order')}
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            headers = {'Location': serializer.data['url']}
            return Response(serializer.data, headers=headers)
        except PaymentError as e:
            return Response({'detail': str(e)}, status=status.HTTP_402_PAYMENT_REQUIRED)

    @action(
        detail=True,
        methods=['post'],
        serializer_class=OrderRefundSerializer,
        permission_classes=[IsAdminUser],
    )
    def refund(self, request, ref):
        """
        Refund all order payments.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if serializer.data['failed']:
            return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
        return Response(serializer.data)
