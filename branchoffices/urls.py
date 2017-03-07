from django.conf.urls import url

from branchoffices import views

app_name = 'branch_offices'

urlpatterns = [
    url(r'^branchoffices/$', views.branch_offices, name='branch_offices'),
]
