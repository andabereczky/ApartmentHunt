from django.conf.urls.defaults import *

urlpatterns = patterns('apartmenthunt.views',
    (r'^$', 'index'),
    (r'^(?P<craigslist_site_id>\d+)/datacollection/$', 'datacollection'),
    (r'^(?P<craigslist_site_id>\d+)/search/$', 'search'),
)
