from django import forms
from django.contrib import admin

from clusters.models import *

class ResourceSelectWidget(forms.MultiWidget):
    choices = ()
    
    def __init__(self, attrs=None):
        all_resources = [('', '----------')] + [(rsc.id, rsc.name) for rsc in EconomicResourceType.objects.all()]
        wrapped_widget = admin.widgets.RelatedFieldWidgetWrapper(
            forms.widgets.Select(attrs=attrs, choices=all_resources),
            FunctionResourceType._meta.get_field('resource_type').rel,
            admin.site,
        ) 
        widgets = (forms.widgets.Select(attrs=attrs),
                   wrapped_widget)
        super(ResourceSelectWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value, value]
        return [None, None]
    
        
    def set_local_choices(self, choices):
        #all_resources = EconomicResourceType.objects.all()
        self.widgets[0].choices = choices
        #self.widgets[1].widget.choices = [('', '----------')] + [(rsc.id, rsc.name) for rsc in all_resources]
        return True
