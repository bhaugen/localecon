from django import forms
from django.contrib import admin

from clusters.models import *

class ResourceChoiceField(forms.ModelChoiceField):

    def __init__(self, *args, **kwargs):
        super(ResourceChoiceField, self).__init__(*args, **kwargs)
        self.widget = admin.widgets.RelatedFieldWidgetWrapper(
            forms.widgets.Select(),
            FunctionResourceType._meta.get_field('resource_type').rel,
            admin.site,
        ) 
        
