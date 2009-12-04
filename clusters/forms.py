from django import forms

from clusters.models import *
from clusters.fields import *

class EconomicFunctionForm(forms.ModelForm):
    
    class Meta:
        model = EconomicFunction
        fields = ('name',)
        

class EconomicResourceTypeForm(forms.ModelForm):
    
    class Meta:
        model = EconomicResourceType
        fields = ('name',)
        

class EconomicAgentForm(forms.ModelForm):
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '80',}))
    
    class Meta:
        model = EconomicAgent
        fields = ('name', 'address')
        

class FunctionResourceTypeFormX(forms.ModelForm):
    resource_type = FunctionResourceChoiceField(EconomicResourceType.objects.none())
        
    class Meta:
        model = FunctionResourceType
        fields = ('resource_type', 'role', 'amount')
        
class FunctionResourceTypeForm(forms.ModelForm):
    amount = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '6', 'value': '0'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    
    def __init__(self, community, *args, **kwargs):
        super(FunctionResourceTypeForm, self).__init__(*args, **kwargs)
        self.fields["resource_type"].queryset = community.resources.all()
        
    class Meta:
        model = FunctionResourceType
        fields = ('resource_type', 'role', 'amount')


class FunctionAgentForm(forms.ModelForm):
    agent = FunctionAgentChoiceField(EconomicAgent.objects.none())
        
    class Meta:
        model = AgentFunction
        fields = ('agent',)
        
class EmailForm(forms.Form):
    email_address = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField(widget = forms.Textarea)
    