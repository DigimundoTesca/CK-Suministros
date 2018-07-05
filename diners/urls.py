from django.conf import settings
from django.conf.urls import url

from diners import views
from diners.views import DinersListView, SuggestionsListView

app_name = 'diners'

urlpatterns = [
    # Diners pin
    url(r'^diners/$', DinersListView.as_view(), name='diners'),
    url(r'^diners/rfid/$', views.register_rfid_diner_log, name='rfid'),
    url(r'^diners/today/$', views.today_access, name='today_access'),
    url(r'^diners/new/$', views.new_diner, name='new_diner'),
    url(r'^diners/logs/$', views.diners_logs, name='diners_logs'),
    url(r'^diners/satisfaction-rating/(?P<pk>[0-9]+)/$', views.satisfaction_rating, name='satisfaction_rating'),
    url(r'^diners/analytics-rating/(?P<pk>[0-9]+)/$', views.analytics_rating, name='analytics'),
    url(r'^diners/suggestions/(?P<pk>[0-9]+)/$', SuggestionsListView.as_view(), name='suggestions'),
]

# Test
if settings.DEBUG:
    urlpatterns.append( url(r'^diners/test/$', views.test, name='diners_test'))
