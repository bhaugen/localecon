import django_filters

from models import *

class AgentFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='contains')
    address = django_filters.CharFilter(lookup_type='contains')
    #communities__community__name = django_filters.CharFilter(label='Community Name', lookup_type='contains')

    class Meta:
        model = EconomicAgent
        #exclude = ('latitude', 'longitude', 'slug')
        fields = ('communities__community',)

    @classmethod
    def queryset(cls):
        return EconomicAgent.objects.select_related().all()

class CommunityAgentFilterSet(django_filters.FilterSet):
    agent__name = django_filters.CharFilter(label="Agent Name", lookup_type='contains')
    agent__address = django_filters.CharFilter(label="Agent Address", lookup_type='contains')

    class Meta:
        model = CommunityAgent
        fields = ('community',)

    @classmethod
    def queryset(cls):
        return CommunityAgent.objects.select_related().all()
    
    
class AgentFunctionResourceTypeFilterSet(django_filters.FilterSet):
    agent_function__agent__name = django_filters.CharFilter(label="Agent Name", lookup_type='contains')
    agent_function__agent__address = django_filters.CharFilter(label="Agent Address", lookup_type='contains')
    agent_function__agent__communities__group = django_filters.AllValuesFilter(label="Agent Group")

    class Meta:
        model = AgentFunctionResourceType
        fields = ('resource_type', 'agent_function__function')
        
    def __init__(self, *args, **kwargs):
            super(AgentFunctionResourceTypeFilterSet, self).__init__(*args, **kwargs)
            qs = kwargs['queryset']
            rtids = list(set(qs.values_list('resource_type', flat=True)))
            rts = EconomicResourceType.objects.filter(id__in=rtids)
            fnids = list(set(qs.values_list('agent_function__function', flat=True)))
            fns = EconomicFunction.objects.filter(id__in=fnids)
            self.filters['resource_type'].field.choices = [('', '----------')] + [(rt.id, rt.name) for rt in rts]
            self.filters['agent_function__function'].field.choices = [('', '----------')] + [(fn.id, fn.name) for fn in fns]

    @classmethod
    def queryset(cls):
        return AgentFunctionResourceType.objects.select_related().all()
    
    @classmethod
    def queryset(cls, cluster):
        return AgentFunctionResourceType.objects.select_related().filter(
                    agent_function__function__cluster=cluster)
        
        
class FunctionResourceTypeFilterSet(django_filters.FilterSet):
    function__name = django_filters.CharFilter(label="Function Name", lookup_type='contains')
    resource_type__name = django_filters.CharFilter(label="Resource Name", lookup_type='contains')
    function__aspect = django_filters.CharFilter(label="Function Aspect", lookup_type='contains')
    resource_type__communities__aspect = django_filters.CharFilter(label="Resource Aspect", lookup_type='contains')


    class Meta:
        model = FunctionResourceType
        #fields = ('function', 'resource_type',)
        
    #def __init__(self, *args, **kwargs):
    #        super(FunctionResourceTypeFilterSet, self).__init__(*args, **kwargs)
    #        qs = kwargs['queryset']
    #        rtids = list(set(qs.values_list('resource_type', flat=True)))
    #        rts = EconomicResourceType.objects.filter(id__in=rtids)
    #        fnids = list(set(qs.values_list('agent_function__function', flat=True)))
    #        fns = EconomicFunction.objects.filter(id__in=fnids)
    #        self.filters['resource_type'].field.choices = [('', '----------')] + [(rt.id, rt.name) for rt in rts]
    #        self.filters['agent_function__function'].field.choices = [('', '----------')] + [(fn.id, fn.name) for fn in fns]

    @classmethod
    def queryset(cls):
        return FunctionResourceType.objects.select_related().all()
    
    @classmethod
    def queryset(cls, cluster):
        return FunctionResourceType.objects.select_related().filter(
                    function__cluster=cluster)
