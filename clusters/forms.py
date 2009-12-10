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
        
        
class ParentedResourceTypeForm(forms.ModelForm):
    
    def __init__(self, function_resource, *args, **kwargs):
        super(AgentResourceForm, self).__init__(*args, **kwargs)
        self.fields["parent"].choices = [('', '----------')] + [
            (res.id, res.name) for res in function_resource.resource_type.all_relatives()
        ]

    
    class Meta:
        model = EconomicResourceType
        fields = ('name', "parent")

class EconomicResourceTypeFormX(forms.ModelForm):
    
    class Meta:
        model = EconomicResourceType
        fields = ('name',)
        
        
    def clean(self):
        cleaned_data = self.cleaned_data
        name = cleaned_data["name"]
        instance = self.instance
        
        try:
            resource = EconomicResourceType.objects.get(name=name)
            cleaned_data["pk"] = resource.pk
        except EconomicResourceType.DoesNotExist:
            pass
        
        #import pdb; pdb.set_trace()
        
        return cleaned_data


class EconomicAgentForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size': '40',}))
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
        self.fields["resource_type"].choices = [('', '----------')] + [
            (cr.resource_type.id, cr.resource_type.name) for cr in community.resources.all()
        ]
        
    class Meta:
        model = FunctionResourceType
        fields = ('resource_type', 'role', 'amount')


class FunctionAgentForm(forms.ModelForm):
    agent = FunctionAgentChoiceField(EconomicAgent.objects.none())
        
    class Meta:
        model = AgentFunction
        fields = ('agent',)

   
class AgentFunctionForm(forms.ModelForm):
    
    def __init__(self, cluster, agent, *args, **kwargs):
        super(AgentFunctionForm, self).__init__(*args, **kwargs)
        used = [(af.function.id) for af in agent.functions.all()]
        self.fields["function"].choices = [
            (fun.id, fun.name) for fun in EconomicFunction.objects.filter(cluster=cluster).exclude(id__in=used)
        ]
        
    class Meta:
        model = AgentFunction
        fields = ('function',)
          

class AgentResourceForm(forms.ModelForm):
    amount = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '6', 'value': '0'}))
    
    def __init__(self, function_resource, *args, **kwargs):
        super(AgentResourceForm, self).__init__(*args, **kwargs)
        self.fields["resource_type"].choices = [('', '----------')] + [
            (res.id, res.name) for res in function_resource.resource_type.all_relatives()
        ]
        self.fields["role"].choices = [(function_resource.role, function_resource.role)]
    
    class Meta:
        model = AgentResourceType
        fields = ('resource_type', 'role', 'amount')

        
class EmailForm(forms.Form):
    email_address = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField(widget = forms.Textarea)
    