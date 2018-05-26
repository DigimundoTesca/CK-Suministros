from django.conf import settings
from django.conf.urls import url

from diners import views
from diners.views import DinersListView

app_name = 'diners'

urlpatterns = [
    # Diners pin
    url(r'^diners/$', DinersListView.as_view(), name='diners'),
    url(r'^diners/rfid/$', views.rfid, name='rfid'),
    url(r'^diners/today/$', views.today_access, name='today_access'),
    url(r'^diners/new/$', views.new_diner, name='new_diner'),
    url(r'^diners/logs/$', views.diners_logs, name='diners_logs'),
    url(r'^diners/satisfaction-rating/$', views.satisfaction_rating, name='satisfaction_rating'),
    url(r'^diners/analytics-rating/$', views.analytics_rating, name='analytics'),
]

# Test
if settings.DEBUG:
    urlpatterns.append( url(r'^diners/test/$', views.test, name='diners_test'))
