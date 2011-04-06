from django.conf.urls.defaults import *
from django.conf import settings

# Enable the admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^apartmenthunt/', include('apartmenthunt.urls')),
	(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
	)
