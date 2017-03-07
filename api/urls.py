from django.conf.urls import url
from . import views

customer_orders = views.CustomerOrderViewSet.as_view({
    'get': 'list',
    'patch': 'partial_update',
})

customer_order_detail = views.CustomerOrderViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
})

customer_order_detail_status = views.CustomerOrderStatusViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
})

customer_order_detail_score = views.CustomerOrderScoreViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
})

customer_order_pin = views.CustomerOrderPinViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
})

urlpatterns = [
    url(r'^v1/customer-orders/$', customer_orders, name='customer_orders_list'),
    url(r'^v1/customer-orders/(?P<pk>[0-9]+)/$', customer_order_detail, name='customer_order_detail'),
    url(r'^v1/customer-orders/(?P<pk>[0-9]+)/status$', customer_order_detail_status,
        name='customer_order_detail_status'),
    url(r'^v1/customer-orders/(?P<pk>[0-9]+)/score', customer_order_detail_score,
        name='customer_order_detail_score'),
    url(r'^v1/customer-orders/(?P<pk>[0-9]+)/pin', customer_order_pin,
        name='customer_order_pin'),
]
