from django.conf import settings
from django.conf.urls import url

from products import views
from products.views import *


app_name = 'products'

urlpatterns = [

    # Supplies
    url(r'^supplies/$', views.supplies, name='supplies'),
    url(r'^supplies/new/$', Create_Supply.as_view(), name='new_supply'),
    url(r'^supplies/(?P<pk>[0-9]+)/$', views.supply_detail, name='supply_detail'),
    url(r'^supplies/modify/(?P<pk>[0-9]+)/$', Update_Supply.as_view(), name='supply_modify'),
    url(r'^supplies/delete/(?P<pk>[0-9]+)/$', Delete_Supply.as_view(), name='supply_delete'),

    # Cartridges
    url(r'^cartridges/$', views.cartridges, name='cartridges'),
    url(r'^cartridges/new/$', Create_Cartridge.as_view(), name='new_cartridge'),
    url(r'^cartridges/(?P<pk>[0-9]+)/$', views.cartridge_detail, name='cartridge_detail'),
    url(r'^cartridges/modify/(?P<pk>[0-9]+)/$', Update_Cartridge.as_view(), name='cartridge_modify'),
    url(r'^cartridges/delete/(?P<pk>[0-9]+)/$', Delete_Cartridge.as_view(), name='cartridge_delete'),

    # Suppliers
    url(r'^suppliers/$', views.suppliers, name='suppliers'),

    # Categories
    url(r'^categories/$', views.categories, name='categories'),
    url(r'^categories/new/$', views.new_category, name='new_category'),
    url(r'^categories/([A-Za-z]+)/$', views.categories_supplies, name='categories_supplies'),
]

# test
if settings.DEBUG:
    urlpatterns.append(url(r'^test/$', views.test, name='test'))
