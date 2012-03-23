from django import forms

from clusters.models import *
from clusters.fields import *

class EconomicFunctionForm(forms.ModelForm):
    
    class Meta:
        model = EconomicFunction
        fields = ('name',)

class InlineAgentFunctionForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size': '24',}))
        
    def __init__(self, cluster, *args, **kwargs):
        super(InlineAgentFunctionForm, self).__init__(*args, **kwargs)
        self.fields["agent"].choices = [('', '----------')] + [
            (agt.id, agt.name) for agt in cluster.agents()
        ]
        
    class Meta:
        model = AgentFunction
        fields = ('agent',)

class ClusterForm(forms.ModelForm):
    
    class Meta:
        model = Cluster
        fields = ('name', 'description')



class CommunityForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size': '40',}))
    map_center = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '80',}))
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    map_zoom_level = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '2',}))
    resource_aspect_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '40',}))
    agent_geographic_area_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '40',}))
    
    class Meta:
        model = Community
        

class EconomicResourceTypeForm(forms.ModelForm):
    
    class Meta:
        model = EconomicResourceType
        fields = ('name', 'unit_of_quantity')
        
        
class ParentedResourceTypeForm(forms.ModelForm):
    
    def __init__(self, function_resource, *args, **kwargs):
        super(ParentedResourceTypeForm, self).__init__(*args, **kwargs)
        self.fields["parent"].choices = [('', '----------')] + [
            (res.id, res.name) for res in function_resource.resource_type.all_relatives()
        ]

    
    class Meta:
        model = EconomicResourceType
        fields = ('name', "parent")

class EconomicResourceTypeFormX(forms.ModelForm):
    
    class Meta:
        model = EconomicResourceType
        fields = ('name', 'unit_of_quantity')
        
        
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
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    
    class Meta:
        model = EconomicAgent
        fields = ('name', 'address', 'latitude', 'longitude')

class AgentAddressForm(forms.ModelForm):
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '40',}))
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    
    class Meta:
        model = EconomicAgent
        fields = ('address', 'latitude', 'longitude')
              

class FunctionResourceTypeFormX(forms.ModelForm):
    resource_type = FunctionResourceChoiceField(EconomicResourceType.objects.none())
        
    class Meta:
        model = FunctionResourceType
        fields = ('resource_type', 'role', 'quantity')
        
class FunctionResourceTypeForm(forms.ModelForm):
    quantity = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '6', 'value': '0'}))
    value = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '6', 'value': '0'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    
    def __init__(self, community, *args, **kwargs):
        super(FunctionResourceTypeForm, self).__init__(*args, **kwargs)
        self.fields["resource_type"].choices = [('', '----------')] + [
            (cr.resource_type.id, cr.resource_type.name) for cr in community.resources.all()
        ]
        
    class Meta:
        model = FunctionResourceType
        fields = ('resource_type', 'role', 'quantity', 'value')

        
class FunctionResourceFlowForm(forms.ModelForm):
    quantity = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '6', 'value': '0'}))
    value = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '6', 'value': '0'}))

        
    class Meta:
        model = FunctionResourceFlow
        
        
class AgentResourceFlowForm(forms.ModelForm):
    quantity = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '6', 'value': '0'}))
    value = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '6', 'value': '0'}))

        
    class Meta:
        model = AgentResourceFlow

        
class FunctionResourceTypeQuantityForm(forms.ModelForm):
    quantity = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '6', 'value': '0'}))
        
    class Meta:
        model = FunctionResourceType
        fields = ('quantity',)


class FunctionAgentForm(forms.ModelForm):
    agent = FunctionAgentChoiceField(EconomicAgent.objects.none())
        
    class Meta:
        model = AgentFunction
        fields = ('agent',)


class AgentFunctionCreationForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'size': '32', 'class': 'function-name'}))


class AgentFunctionForm(forms.ModelForm):
    
    def __init__(self, cluster, agent, *args, **kwargs):
        super(AgentFunctionForm, self).__init__(*args, **kwargs)
        used = [(af.function.id) for af in agent.functions.all()]
        self.fields["function"].choices = [('', '----------')] + [
            (fun.id, fun.name) for fun in EconomicFunction.objects.filter(cluster=cluster).exclude(id__in=used)
        ]
        
    class Meta:
        model = AgentFunction
        fields = ('function',)
          

class AgentResourceForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size': '16', 'class': 'resource-name'}))
    quantity = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '6', 'value': '0'}))
    
    def __init__(self, function_resource=None, *args, **kwargs):
        super(AgentResourceForm, self).__init__(*args, **kwargs)
        if function_resource:
            self.fields["role"].choices = [(function_resource.role, function_resource.role)]
    
    class Meta:
        model = AgentResourceType
        fields = ('role', 'quantity')


class AgentFunctionResourceForm(forms.ModelForm):
    agent_function_id = forms.IntegerField(widget=forms.HiddenInput)
    name = forms.CharField(widget=forms.TextInput(attrs={'size': '16', 'class': 'resource-name'}))
    quantity = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '7', 'value': '0'}))
    value = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '7', 'value': '0'}))
    
    def __init__(self, function_resource=None, *args, **kwargs):
        super(AgentFunctionResourceForm, self).__init__(*args, **kwargs)
        if function_resource:
            self.fields["role"].choices = [(function_resource.role, function_resource.role)]
    
    class Meta:
        model = AgentFunctionResourceType
        fields = ('role', 'quantity', 'value')

        
class EmailForm(forms.Form):
    email_address = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField(widget = forms.Textarea)
    
    
TOGGLE_CHOICES = (
    ('qty', 'Quantity or'),
    ('val', 'Value'),
) 

class QuantityValueForm(forms.Form):
    toggle = forms.ChoiceField(choices=TOGGLE_CHOICES, widget=forms.RadioSelect(attrs={'class': 'tog'}))
    
LEVEL_CHOICES = (
    ('fn', 'Functions or'),
    ('agt', 'Agents'),
) 

class FunctionAgentForm(forms.Form):
    level = forms.ChoiceField(choices=LEVEL_CHOICES, widget=forms.RadioSelect(attrs={'class': 'tog'}))

    