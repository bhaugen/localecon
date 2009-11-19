from django import forms

from clusters.models import *

class ResourceSelectWidget(forms.MultiWidget):
    choices = ()
    local_choices = EconomicResourceType.objects.none()
    all_choices = EconomicResourceType.objects.all()
    
    def __init__(self, attrs=None):

        widgets = (forms.widgets.Select(attrs=attrs, choices=self.local_choices),
                   forms.widgets.Select(attrs=attrs, choices=self.all_choices))
        super(ResourceSelectWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value, value]
        return [None, None]
    
    def set_local_choices(self, choices):
        self.local_choices = choices
        widgets[0].choices = choices
        return True
        
    
