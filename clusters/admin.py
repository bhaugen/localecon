from django.contrib import admin
from clusters.models import *
from clusters.actions import export_as_csv

admin.site.add_action(export_as_csv, 'export_selected objects')

admin.site.register(Community)

class ClusterAdmin(admin.ModelAdmin):
    list_display = ('name', 'community', 'created_by', 'sharing')
    list_filter = ['created_by', 'sharing']
    
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
    list_display = ('name', 'cluster', 'aspect')
    list_filter = ['cluster',]
    search_fields = ['name', 'cluster__name']
    list_editable = ['aspect', 'color',]
    inlines = [ 
               FunctionResourceInline,
               IncomingFunctionResourceFlowInline,
               OutgoingFunctionResourceFlowInline, 
               ]
    
admin.site.register(EconomicFunction, EconomicFunctionAdmin)

class AgentFunctionInline(admin.TabularInline):
    model = AgentFunction

class AgentFunctionResourceInline(admin.TabularInline):
    model = AgentFunctionResourceType


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
    inlines = [AgentFunctionInline,]
    
admin.site.register(EconomicAgent, EconomicAgentAdmin)


class AgentFunctionAdmin(admin.ModelAdmin):
    list_display = ('agent', 'function')
    inlines = [AgentFunctionResourceInline,
               IncomingAgentResourceFlowInline,
               OutgoingAgentResourceFlowInline,
               ]
    
admin.site.register(AgentFunction, AgentFunctionAdmin)


class EconomicResourceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    list_filter = ['parent']
    search_fields = ['name',]
    
admin.site.register(EconomicResourceType, EconomicResourceTypeAdmin)


class CommunityResourceTypeAdmin(admin.ModelAdmin):
    list_display = ('community', 'resource_type', 'aspect')
    list_filter = ['community']
    list_editable = ['aspect',]
    search_fields = ['community__name', 'resource_type__name']

admin.site.register(CommunityResourceType, CommunityResourceTypeAdmin)

class CommunityAgentAdmin(admin.ModelAdmin):
    list_display = ('community', 'agent', 'group', 'geographic_area')
    list_filter = ['community']
    list_editable = ['group', 'geographic_area']
    search_fields = ['community__name', 'agent__name']

admin.site.register(CommunityAgent, CommunityAgentAdmin)

class CommunityMemberAdmin(admin.ModelAdmin):
    list_display = ('community', 'member', 'permission_role')
    list_filter = ['community']
    
admin.site.register(CommunityMember, CommunityMemberAdmin)

admin.site.register(SiteSettings)
admin.site.register(Unit)
