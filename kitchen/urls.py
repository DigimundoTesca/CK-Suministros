from django.conf.urls import url

from kitchen import views

app_name = 'kitchen'

urlpatterns = [
    # Warehouse
    # url(r'warehouse/$', views.supplies, name='supplies'),

    # Kitchen
    # url(r'kitchen/$', views.kitchen, name='kitchen'),
    # url(r'kitchen/assembly/$', views.assembly, name='assembly'),
]
