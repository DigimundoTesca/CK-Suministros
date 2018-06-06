from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^admin-cloud/', admin.site.urls, name='admin'),
    url(r'^', include('users.urls')),
     url(r'^', include('branchoffices.urls')),
    url(r'^', include('products.urls')),
    url(r'^', include('sales.urls')),
    # url(r'^', include('orders.urls')),
    url(r'^', include('kitchen.urls')),
    url(r'^', include('diners.urls')),
]

admin.site.site_header = 'CloudKitchen'

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)),]

urlpatterns += [
    # API Endpoints
    # url(r'^api/', include('api.urls', namespace='api')),
]