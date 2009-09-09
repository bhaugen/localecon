from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # clusters
    url(r'^$', 'clusters.views.clusters', name="clusters"),
    url(r'^cluster/(?P<cluster_id>\d+)/$', 'clusters.views.cluster', name="cluster"),
)

