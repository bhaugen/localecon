from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # clusters
    url(r'^$', 'clusters.views.clusters', name="clusters"),
    url(r'^cluster/(?P<cluster_id>\d+)/$', 'clusters.views.cluster', name="cluster"),
    url(r'^rgraph/(?P<cluster_id>\d+)/$', 'clusters.views.radial_graph', name="radial_graph"),
    url(r'^iotable/(?P<cluster_id>\d+)/$', 'clusters.views.iotable', name="iotable"),
    url(r'^frtable/(?P<cluster_id>\d+)/$', 'clusters.views.fr_table', name="fr_table"),
    
    # agents
    url(r'^clusteragents/(?P<cluster_id>\d+)/$', 'clusters.views.cluster_agents', name="cluster_agents"),
    url(r'^newclusteragent/(?P<cluster_id>\d+)/$', 'clusters.views.new_cluster_agent', name="new_cluster_agent"),
    url(r'^jsonagentaddress/(?P<agent_name>[-\w]+)/$', 'clusters.views.json_agent_address', name="json_agent_address"),
    
    
    # functions
    url(r'^functions/(?P<cluster_id>\d+)/$', 'clusters.views.economic_functions', name="economic_functions"),
    url(r'^function/(?P<function_id>\d+)/$', 'clusters.views.economic_function', name="economic_function"),
    url(r'^newfunction/(?P<cluster_id>\d+)/$', 'clusters.views.new_function', name="new_function"),
    url(r'^inlinenewfunction/(?P<cluster_id>\d+)/$', 'clusters.views.inline_new_function', name="inline_new_function"),
    url(r'^editclusterfunctions/(?P<cluster_id>\d+)/$', 'clusters.views.edit_cluster_functions', name="edit_cluster_functions"),
    
    # resources
    url(r'^inlinenewresource/(?P<cluster_id>\d+)/$', 'clusters.views.inline_new_resource', name="inline_new_resource"),
    url(r'^newresource/(?P<cluster_id>\d+)/$', 'clusters.views.new_resource', name="new_resource"),
    
    #function resources
    url(r'^newfunctionresource/(?P<function_id>\d+)/$', 'clusters.views.new_function_resource', name="new_function_resource"),
)

