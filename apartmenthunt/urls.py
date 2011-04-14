from django.conf.urls.defaults import *

urlpatterns = patterns('apartmenthunt.views',
    (r'^$', 'index'),
    (r'^(?P<craigslist_site_subdomain>\w+)/search/$', 'search'),
)
