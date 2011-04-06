from django.conf.urls.defaults import *

# Enable the admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^Project/', include('Project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
