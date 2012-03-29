import django_filters

from models import *

class AgentFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='contains')
    communities__name = django_filters.CharFilter(label='Community Name', lookup_type='contains')

    class Meta:
        model = EconomicAgent

    @classmethod
    def queryset(cls):
        return EconomicAgent.objects.select_related().all()
