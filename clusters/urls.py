from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # clusters
    url(r'^$', 'clusters.views.clusters', name="clusters"),
    url(r'^cluster/(?P<cluster_id>\d+)/$', 'clusters.views.cluster', name="cluster"),
    url(r'^iotable/(?P<cluster_id>\d+)/$', 'clusters.views.iotable', name="iotable"),
    url(r'^frtable/(?P<cluster_id>\d+)/$', 'clusters.views.fr_table', name="fr_table"),
    
    # functions
    url(r'^functions/(?P<cluster_id>\d+)/$', 'clusters.views.economic_functions', name="economic_functions"),
    url(r'^function/(?P<function_id>\d+)/$', 'clusters.views.economic_function', name="economic_function"),
    url(r'^newfunction/(?P<cluster_id>\d+)/$', 'clusters.views.new_function', name="new_function"),
)

