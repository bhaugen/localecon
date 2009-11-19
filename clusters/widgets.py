from django import forms

from clusters.models import *

class ResourceSelectWidget(forms.MultiWidget):
    choices = EconomicResourceType.objects.none()
    #all_choices = EconomicResourceType.objects.all()
    
    def __init__(self, attrs=None):

        widgets = (forms.widgets.Select(attrs=attrs, choices=EconomicResourceType.objects.none()),
                   forms.widgets.Select(attrs=attrs, choices=EconomicResourceType.objects.all()))
        super(ResourceSelectWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value, value]
        return [None, None]
    
        
    def set_local_choices(self, choices):
        self.widgets[0].choices = choices
        return True
