from django import forms

from clusters.models import *

class ResourceSelectWidget(forms.MultiWidget):
    choices = ()
    #all_choices = EconomicResourceType.objects.all()
    
    def __init__(self, attrs=None):
        all_resources = list(EconomicResourceType.objects.all())
        widgets = (forms.widgets.Select(attrs=attrs, choices=()),
                   forms.widgets.Select(attrs=attrs, choices=all_resources))
        super(ResourceSelectWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value, value]
        return [None, None]
    
        
    def set_local_choices(self, choices):
        self.widgets[0].choices = choices
        return True
