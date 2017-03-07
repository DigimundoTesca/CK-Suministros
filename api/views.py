from rest_framework import viewsets, status

from api.serializers import CustomerOrderSerializer, CustomerOrderStatusSerializer, CustomerOrderScoreSerializer, \
    CustomerOrderPinSerializer
from orders.models import CustomerOrder


class CustomerOrderViewSet(viewsets.ModelViewSet):
    queryset = CustomerOrder.objects.all()
    serializer_class = CustomerOrderSerializer


class CustomerOrderStatusViewSet(viewsets.ModelViewSet):
    queryset = CustomerOrder.objects.all()
    serializer_class = CustomerOrderStatusSerializer


class CustomerOrderScoreViewSet(viewsets.ModelViewSet):
    queryset = CustomerOrder.objects.all()
    serializer_class = CustomerOrderScoreSerializer


class CustomerOrderPinViewSet(viewsets.ModelViewSet):
    queryset = CustomerOrder.objects.all()
    serializer_class = CustomerOrderPinSerializer