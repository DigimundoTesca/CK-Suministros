from django.conf import settings
from django.conf.urls import url

from diners import views


app_name = 'diners'

urlpatterns = [
    # Diners pin
    url(r'^diners/rfid/$', views.RFID, name='rfid'),
    url(r'^diners/$', views.diners, name='diners'),
]
