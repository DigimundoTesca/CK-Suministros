from django.conf.urls import url

from kitchen import views

app_name = 'kitchen'

urlpatterns = [
    # Warehouse
    # url(r'warehouse/$', views.supplies, name='supplies'),

    # Kitchen
    url(r'kitchen/cold/$', views.cold_kitchen, name='cold_kitchen'),
    url(r'kitchen/hot/$', views.hot_kitchen, name='hot_kitchen'),
    url(r'kitchen/assembly/$', views.assembly, name='assembly'),
]
