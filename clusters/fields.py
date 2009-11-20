from django import forms
from django.contrib import admin

from clusters.models import *
from clusters.widgets import *

#class ChoicesWrapper(admin.widgets.RelatedFieldWidgetWrapper):
    

class FunctionResourceChoiceFieldX(forms.ModelChoiceField):

    def __init__(self, *args, **kwargs):
        super(FunctionResourceChoiceField, self).__init__(*args, **kwargs)
        self.widget = admin.widgets.RelatedFieldWidgetWrapper(
            #forms.widgets.Select(),
            ResourceSelectWidget(),
            FunctionResourceType._meta.get_field('resource_type').rel,
            admin.site,
        ) 
        
class FunctionResourceChoiceField(forms.MultiValueField):
    widget = ResourceSelectWidget

    def __init__(self, *args, **kwargs):
        all_resources = [('', '----------')] + [(rsc.id, rsc.name) for rsc in EconomicResourceType.objects.all()]
        fields = (
            forms.ChoiceField(),
            forms.ChoiceField(choices=all_resources),
        )
        super(FunctionResourceChoiceField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return data_list
        return None


class FunctionAgentChoiceField(forms.ModelChoiceField):

    def __init__(self, *args, **kwargs):
        super(FunctionAgentChoiceField, self).__init__(*args, **kwargs)
        self.widget = admin.widgets.RelatedFieldWidgetWrapper(
            forms.widgets.Select(),
            AgentFunction._meta.get_field('agent').rel,
            admin.site,
        ) 


class AgentResourceChoiceField(forms.ModelChoiceField):

    def __init__(self, *args, **kwargs):
        super(AgentResourceChoiceField, self).__init__(*args, **kwargs)
        self.widget = admin.widgets.RelatedFieldWidgetWrapper(
            forms.widgets.Select(),
            AgentResourceType._meta.get_field('resource_type').rel,
            admin.site,
        ) 


class AgentFunctionChoiceField(forms.ModelChoiceField):

    def __init__(self, *args, **kwargs):
        super(AgentFunctionChoiceField, self).__init__(*args, **kwargs)
        self.widget = admin.widgets.RelatedFieldWidgetWrapper(
            forms.widgets.Select(),
            AgentFunction._meta.get_field('function').rel,
            admin.site,
        ) 
