from django.conf import settings
from django.conf.urls import url

from diners import views


app_name = 'diners'

urlpatterns = [
    # Diners pin
    url(r'^diners/pin/(?P<pin>[^/]+)/(?P<date>[^/]+)$', views.pin, name='pin'),
    url(r'^diners/$', views.diners, name='diners'),

]
