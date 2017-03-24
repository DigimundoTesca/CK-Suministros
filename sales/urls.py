from django.conf import settings
from django.conf.urls import url

from sales import views

app_name = 'sales'

urlpatterns = [
    # sales
    url(r'^sales/$', views.sales, name='sales'),
    url(r'^sales/new/food/$', views.new_sale, name='new_food'),
    url(r'^sales/new/breakfast/$', views.new_sale, name='new_breakfast'),
    url(r'^sales/delete/$', views.delete_sale, name='delete-sale'),
]

if settings.DEBUG:
    urlpatterns.append(url('^sales/test/$', views.test, name='test'))

