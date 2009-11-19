from django import forms

class ResourceSelectWidget(forms.MultiWidget):
    choices = EconomicResourceType.objects.none()
    
    def __init__(self, attrs=None):

        widgets = (forms.widgets.Select(attrs=attrs),
                   forms.widgets.Select(attrs=attrs))
        super(ResourceSelectWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value, value]
        return [None, None]
    
