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
