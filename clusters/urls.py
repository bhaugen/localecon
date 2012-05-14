from django.conf.urls.defaults import *

from models import *
from filter_defs import *

urlpatterns = patterns('',
                       
    #communities
    url(r'^newcommunity/$', 'clusters.views.new_community', name="new_community"),
    url(r'^editcommunity/(?P<community_id>\d+)/$', 'clusters.views.edit_community', name="edit_community"),
    
    # clusters
    url(r'^$', 'clusters.views.clusters', name="clusters"),
    url(r'^newcluster/(?P<community_id>\d+)/$', 'clusters.views.new_cluster', name="new_cluster"),
    url(r'^editcluster/(?P<cluster_id>\d+)/$', 'clusters.views.edit_cluster', name="edit_cluster"),
    url(r'^cluster/(?P<cluster_id>\d+)/$', 'clusters.views.cluster', name="cluster"),
    url(r'^cluster/(?P<cluster_id>\d+)/(?P<location>\w+)/$', 'clusters.views.cluster', name="cluster"),
    url(r'^rgraph/(?P<cluster_id>\d+)/$', 'clusters.views.radial_graph', name="radial_graph"),
    url(r'^iotable/(?P<cluster_id>\d+)/$', 'clusters.views.iotable', name="iotable"),
    url(r'^frtable/(?P<cluster_id>\d+)/$', 'clusters.views.fr_table', name="fr_table"),
    url(r'^frtable/(?P<cluster_id>\d+)/(?P<toggle>\w+)/$', 'clusters.views.fr_table', name="fr_table"),
    url(r'^diagnostics/(?P<cluster_id>\d+)/$', 'clusters.views.diagnostics', name="diagnostics"),
    url(r'^diagnostics/(?P<cluster_id>\d+)/(?P<level>\w+)/$', 'clusters.views.diagnostics', name="diagnostics"),
    url(r'^modelerrors/(?P<cluster_id>\d+)/$', 'clusters.views.model_errors', name="model_errors"),
    url(r'^network/(?P<cluster_id>\d+)/$', 'clusters.views.network', name="network"),
    url(r'^network/(?P<cluster_id>\d+)/(?P<toggle>\w+)/$', 'clusters.views.network', name="network"),
    url(r'^network/(?P<cluster_id>\d+)/(?P<toggle>\w+)/(?P<level>\w+)/$', 'clusters.views.network', name="network"),
    url(r'^flows/(?P<cluster_id>\d+)/$', 'clusters.views.flows', name="flows"),
    url(r'^flows/(?P<cluster_id>\d+)/(?P<toggle>\w+)/$', 'clusters.views.flows', name="flows"),
    url(r'^flows/(?P<cluster_id>\d+)/(?P<toggle>\w+)/(?P<level>\w+)/$', 'clusters.views.flows', name="flows"),
    url(r'^explore/(?P<cluster_id>\d+)/$', 'clusters.views.explore', name="explore"),


    # agents
    url(r'^clusteragents/(?P<cluster_id>\d+)/$', 'clusters.views.cluster_agents', name="cluster_agents"),
    url(r'^newclusteragent/(?P<cluster_id>\d+)/$', 'clusters.views.new_cluster_agent', name="new_cluster_agent"),
    url(r'^editclusteragent/(?P<cluster_id>\d+)/(?P<agent_id>\d+)/$', 'clusters.views.edit_cluster_agent', name="edit_cluster_agent"),
    url(r'^editagentflows/(?P<cluster_id>\d+)/$', 'clusters.views.edit_agent_flows', name="edit_agent_flows"),
    url(r'^editagentaddress/(?P<cluster_id>\d+)/(?P<agent_id>\d+)/$', 'clusters.views.edit_agent_address', name="edit_agent_address"),
    url(r'^editcommunityagent/(?P<cluster_id>\d+)/(?P<agent_id>\d+)/$', 'clusters.views.edit_community_agent', name="edit_community_agent"),
    url(r'^inlinenewagentfunction/(?P<cluster_id>\d+)/(?P<agent_id>\d+)/$', 'clusters.views.inline_new_agent_function', name="inline_new_agent_function"),
    url(r'^jsonagentaddress/(?P<agent_name>.+)/$', 'clusters.views.json_agent_address', name="json_agent_address"),
    url(r'^newagentfunction/(?P<cluster_id>\d+)/$', 'clusters.views.new_agent_function', name="new_agent_function"),
    
    
    # functions
    url(r'^functions/(?P<cluster_id>\d+)/$', 'clusters.views.economic_functions', name="economic_functions"),
    url(r'^function/(?P<function_id>\d+)/$', 'clusters.views.economic_function', name="economic_function"),
    url(r'^newfunction/(?P<cluster_id>\d+)/$', 'clusters.views.new_function', name="new_function"),
    url(r'^editfunction/(?P<function_id>\d+)/$', 'clusters.views.edit_function', name="edit_function"),
    url(r'^deletefunction/(?P<function_id>\d+)/$', 'clusters.views.delete_function', name="delete_function"),
    url(r'^deletefunctionconfirmation/(?P<function_id>\d+)/$', 'clusters.views.delete_function_confirmation', 
        name="delete_function_confirmation"),
    url(r'^inlinenewfunction/(?P<cluster_id>\d+)/$', 'clusters.views.inline_new_function', name="inline_new_function"),
    url(r'^editclusterfunctions/(?P<cluster_id>\d+)/$', 'clusters.views.edit_cluster_functions', name="edit_cluster_functions"),
    url(r'^editflows/(?P<cluster_id>\d+)/$', 'clusters.views.edit_flows', name="edit_flows"),
    url(r'^jsonfunctionaspect/(?P<function_name>.+)/(?P<cluster_id>\d+)/$', 'clusters.views.json_function_aspect', name="json_function_aspect"),
    
    # resources
    url(r'^inlinenewresource/(?P<cluster_id>\d+)/$', 'clusters.views.inline_new_resource', name="inline_new_resource"),
    url(r'^inlineagentresource/(?P<cluster_id>\d+)/(?P<agent_id>\d+)/(?P<parent_id>\d+)/$', 'clusters.views.inline_agent_resource', name="inline_agent_resource"),
    url(r'^newresource/(?P<cluster_id>\d+)/$', 'clusters.views.new_resource', name="new_resource"),
    url(r'^jsonresourceunit/(?P<name>.+)/$', 'clusters.views.json_resource_unit', name="json_resource_unit"),
    url(r'^jsonresourceaspect/(?P<name>.+)/(?P<community_id>\d+)/$', 'clusters.views.json_resource_aspect', name="json_resource_aspect"),
    
    #function resources
    url(r'^newfunctionresource/(?P<function_id>\d+)/$', 'clusters.views.new_function_resource', name="new_function_resource"),
    url(r'^deletefunctionresource/(?P<id>\d+)/$', 'clusters.views.delete_function_resource', name="delete_function_resource"),
    url(r'^changefunctionresourceamount/$', 'clusters.views.change_function_resource_amount', 
        name="change_function_resource_amount"),
    url(r'^changefunctionresourcevalue/$', 'clusters.views.change_function_resource_value', 
        name="change_function_resource_value"),
    url(r'^changefunctionresourceprice/$', 'clusters.views.change_function_resource_price', 
        name="change_function_resource_price"),
        
    url(r'^deleteagentfunctionresource/(?P<id>\d+)/$', 'clusters.views.delete_agent_function_resource', 
        name="delete_agent_function_resource"),
    url(r'^changeagentfunctionresourceamount/$', 'clusters.views.change_agent_function_resource_amount', 
        name="change_agent_function_resource_amount"),
    url(r'^changeagentfunctionresourcevalue/$', 'clusters.views.change_agent_function_resource_value', 
        name="change_agent_function_resource_value"),
    url(r'^changeagentfunctionresourceprice/$', 'clusters.views.change_agent_function_resource_price', 
        name="change_agent_function_resource_price"),
        
    #reports
    url(r'^agentreport/$', 
         'clusters.views.object_filter',
         {'model': EconomicAgent, 'filter_class': AgentFilterSet, 'queryset': AgentFilterSet.queryset() }),
    url(r'^communityagentreport/$', 
         'clusters.views.object_filter',
         {'model': CommunityAgent, 'filter_class': CommunityAgentFilterSet, 'queryset': CommunityAgentFilterSet.queryset() }),
    url(r'^agentfunctionreport/(?P<cluster_id>\d+)/$', 
         'clusters.views.object_filter',
         {'model': AgentFunctionResourceType, 'filter_class': AgentFunctionResourceTypeFilterSet}),
    url(r'^functionresourcereport/(?P<cluster_id>\d+)/$', 
         'clusters.views.object_filter',
         {'model': FunctionResourceType, 'filter_class': FunctionResourceTypeFilterSet}),
    url(r'^valueaddedreport/(?P<cluster_id>\d+)/$', 'clusters.views.value_added_report', name="value_added_report"),
)

