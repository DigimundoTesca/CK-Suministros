from django.conf import settings
from django.conf.urls import url

from users import views

app_name = 'users'

urlpatterns = [
    # index
    url(r'^$', views.index, name='index'),

    # auth
    url(r'^auth/$', views.login, name='login'),
    url(r'^auth/logout/$', views.logout, name='logout'),
    url(r'^auth/login_register/$', views.login_register, name='login_register'),

    # New Customer
    url(r'^register/$', views.new_customer, name='new_customer'),
    url(r'^register/thanks/$', views.thanks, name='thanks'),
    url(r'^customers/register/list/$', views.customers_list, name='customers_list'),
    

    # profile
    # url(r'^profiles/$', views.ProfileVIew, name='profiles'),

    # test
]

if settings.DEBUG:
    urlpatterns.append(url(r'^customers/test', views.test, name='cutomers_test'))