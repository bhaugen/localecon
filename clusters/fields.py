from django import forms
from django.contrib import admin

from clusters.models import *
from clusters.widgets import *

class FunctionResourceChoiceField(forms.ModelChoiceField):

    def __init__(self, *args, **kwargs):
        super(FunctionResourceChoiceField, self).__init__(*args, **kwargs)
        self.widget = admin.widgets.RelatedFieldWidgetWrapper(
            #forms.widgets.Select(),
            ResourceSelectWidget(),
            FunctionResourceType._meta.get_field('resource_type').rel,
            admin.site,
        ) 
        

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
