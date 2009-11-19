from django import forms

from clusters.models import *
from clusters.fields import *

class EconomicFunctionForm(forms.ModelForm):
    
    class Meta:
        model = EconomicFunction
        fields = ('name',)
        
        
class FunctionResourceTypeForm(forms.ModelForm):
    resource_type = FunctionResourceChoiceField(EconomicResourceType.objects.none())
        
    class Meta:
        model = FunctionResourceType
        fields = ('resource_type', 'role', 'amount')



        
class EmailForm(forms.Form):
    email_address = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField(widget = forms.Textarea)
    