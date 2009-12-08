from django.contrib import admin
from clusters.models import *
from clusters.forms import EconomicResourceTypeFormX

admin.site.register(Community)

class ClusterAdmin(admin.ModelAdmin):
    list_display = ('name', 'community')
    
admin.site.register(Cluster, ClusterAdmin)

class FunctionResourceInline(admin.TabularInline):
    model = FunctionResourceType


class EconomicFunctionAdmin(admin.ModelAdmin):
    list_display = ('name', 'cluster')
    list_filter = ['cluster',]
    search_fields = ['name', 'cluster']
    inlines = [ FunctionResourceInline, ]
    
admin.site.register(EconomicFunction, EconomicFunctionAdmin)

class AgentFunctionInline(admin.TabularInline):
    model = AgentFunction

class AgentResourceInline(admin.TabularInline):
    model = AgentResourceType

class EconomicAgentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ['name',]
    search_fields = ['name',]
    inlines = [ AgentFunctionInline, AgentResourceInline]
    
admin.site.register(EconomicAgent, EconomicAgentAdmin)

class EconomicResourceTypeAdmin(admin.ModelAdmin):
    form = EconomicResourceTypeFormX
    list_display = ('name',)
    list_filter = ['name',]
    search_fields = ['name',]
    
admin.site.register(EconomicResourceType, EconomicResourceTypeAdmin)

admin.site.register(SiteSettings)
admin.site.register(CommunityResourceType)
admin.site.register(CommunityAgent)

