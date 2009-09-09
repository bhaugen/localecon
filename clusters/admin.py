from django.contrib import admin
from clusters.models import *

admin.site.register(Community)
admin.site.register(Cluster)

class FunctionResourceInline(admin.TabularInline):
    model = FunctionResourceType


class EconomicFunctionAdmin(admin.ModelAdmin):
    list_display = ('name', 'cluster')
    list_filter = ['cluster',]
    search_fields = ['name', 'cluster']
    inlines = [ FunctionResourceInline, ]
    
admin.site.register(EconomicFunction, EconomicFunctionAdmin)

admin.site.register(EconomicResourceType)
admin.site.register(EconomicAgent)
admin.site.register(AgentFunction)
admin.site.register(AgentResourceType)
admin.site.register(CommunityResourceType)
admin.site.register(CommunityAgent)

