from django.contrib import admin
from clusters.models import *

admin.site.register(Community)

class ClusterAdmin(admin.ModelAdmin):
    list_display = ('name', 'community')
    
admin.site.register(Cluster, ClusterAdmin)

class FunctionResourceInline(admin.TabularInline):
    model = FunctionResourceType


class IncomingFunctionResourceFlowInline(admin.TabularInline):
    model = FunctionResourceFlow
    fk_name = 'to_function'
    verbose_name = 'incoming flow'
    verbose_name_plural = 'incoming flows'


class OutgoingFunctionResourceFlowInline(admin.TabularInline):
    model = FunctionResourceFlow
    fk_name = 'from_function'
    verbose_name = 'outgoing flow'
    verbose_name_plural = 'outgoing flows'


class EconomicFunctionAdmin(admin.ModelAdmin):
    list_display = ('name', 'cluster')
    list_filter = ['cluster',]
    search_fields = ['name', 'cluster']
    inlines = [ 
               FunctionResourceInline,
               IncomingFunctionResourceFlowInline,
               OutgoingFunctionResourceFlowInline, 
               ]
    
admin.site.register(EconomicFunction, EconomicFunctionAdmin)

class AgentFunctionInline(admin.TabularInline):
    model = AgentFunction

class AgentResourceInline(admin.TabularInline):
    model = AgentResourceType


class IncomingAgentResourceFlowInline(admin.TabularInline):
    model = AgentResourceFlow
    fk_name = 'to_function'
    verbose_name = 'incoming flow'
    verbose_name_plural = 'incoming flows'


class OutgoingAgentResourceFlowInline(admin.TabularInline):
    model = AgentResourceFlow
    fk_name = 'from_function'
    verbose_name = 'outgoing flow'
    verbose_name_plural = 'outgoing flows'

class EconomicAgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ['name', 'address']
    inlines = [ AgentFunctionInline, 
               AgentResourceInline,
               ]
    
admin.site.register(EconomicAgent, EconomicAgentAdmin)


class AgentFunctionAdmin(admin.ModelAdmin):
    list_display = ('agent', 'function')
    inlines = [IncomingAgentResourceFlowInline,
               OutgoingAgentResourceFlowInline,
               ]
    
admin.site.register(AgentFunction, AgentFunctionAdmin)


class EconomicResourceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    list_filter = ['parent']
    search_fields = ['name', 'parent']
    
admin.site.register(EconomicResourceType, EconomicResourceTypeAdmin)


class CommunityResourceTypeAdmin(admin.ModelAdmin):
    list_display = ('community', 'resource_type')
    list_filter = ['community']
    search_fields = ['community', 'resource_type']

admin.site.register(CommunityResourceType, CommunityResourceTypeAdmin)

admin.site.register(SiteSettings)
admin.site.register(CommunityAgent)
admin.site.register(Unit)
