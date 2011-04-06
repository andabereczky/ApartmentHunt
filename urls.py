from django.conf.urls.defaults import *

# Enable the admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^apartmenthunt/', include('apartmenthunt.urls')),
	(r'^admin/', include(admin.site.urls)),
)
