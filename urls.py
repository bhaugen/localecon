from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.contrib import admin

import os.path

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'clusters.views.featured_cluster', name="featured_cluster"),
    (r'^clusters/', include('clusters.urls')),
        
    # admin
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    
    # emails
    url(r'^sendemail/$', 'clusters.views.send_email', name="send_email"),
    url(r'^email_sent/$', direct_to_template, 
        {"template": "clusters/email_sent.html"}, name="email_sent"),
        
    # about
    #url(r'^about/$', direct_to_template, 
    #    {"template": "about.html"}, name="about"),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(os.path.dirname(__file__), "site_media")}),
    )