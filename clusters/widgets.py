from django import forms

from clusters.models import *

class ResourceSelectWidget(forms.MultiWidget):
    choices = ()
    
    def __init__(self, attrs=None):
        widgets = (forms.widgets.Select(attrs=attrs),
                   forms.widgets.Select(attrs=attrs))
        super(ResourceSelectWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value, value]
        return [None, None]
    
        
    def set_local_choices(self, choices):
        all_resources = EconomicResourceType.objects.all()
        self.widgets[0].choices = choices
        self.widgets[1].choices = [('', '----------')] + [(rsc.id, rsc.name) for rsc in all_resources]
        return True
