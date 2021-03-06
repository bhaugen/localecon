try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = None

from django import forms
from django.conf import settings

from clusters.models import *
from clusters.fields import *

class EconomicFunctionForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size': '24', 'class': 'function-name'}))
    aspect = forms.CharField(required=False)
    color = forms.ChoiceField(choices=settings.COLOR_CHOICES)
    
    class Meta:
        model = EconomicFunction
        fields = ('name', 'aspect', 'color')

class InlineAgentFunctionForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size': '24', 'class': 'function-name'}))
    aspect = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '24', 'class': 'function-aspect'}))
        
    def __init__(self, cluster, *args, **kwargs):
        super(InlineAgentFunctionForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        self.fields["agent"].choices = [('', '----------')] + [
            (agt.id, agt.name) for agt in cluster.agents()
        ]
        
    class Meta:
        model = AgentFunction
        fields = ('agent',)

class ClusterForm(forms.ModelForm):
    function_aspect_name = forms.CharField(required=False)
    description = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '80', 'value': ''}))
    
    class Meta:
        model = Cluster
        fields = ('name', 'description', 'function_aspect_name', 'sharing')



class CommunityForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size': '40',}))
    description = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '80', 'value': ''}))
    map_center = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '80',}))
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    map_zoom_level = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '2',}))
    resource_aspect_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '40',}))
    agent_geographic_area_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '40',}))
    
    class Meta:
        model = Community


class EconomicResourceTypeForm(forms.ModelForm):
    aspect = forms.CharField(required=False)
    
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
    geographic_area = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '80',}))
    group = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '40',}))
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    region_latitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    region_longitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    
    class Meta:
        model = EconomicAgent
        fields = ('name', 'address', 'latitude', 'longitude')


class AgentTextForm(forms.ModelForm):
    description = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '40', 'rows': '4', 'value': ''}))
    text_info_provided_by = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '10',}))
    text_contact = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '10',}))
    text_degree_of_separation = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '5',}))
    text_consumes = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '40', 'rows': '4', 'value': ''}))
    text_produces = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '40', 'rows': '4', 'value': ''}))
    
    class Meta:
        model = EconomicAgent
        fields = ('description', 'text_info_provided_by', 'text_contact', 'text_degree_of_separation', 'text_consumes', 'text_produces')        
        
        
class EditCommunityAgentForm(forms.ModelForm):
    geographic_area = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '80',}))
    group = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '40',}))
    region_latitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    region_longitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    
    class Meta:
        model = CommunityAgent
        exclude = ('community', 'agent')


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
    quantity = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '6', 'value': '1'}))
    price = forms.DecimalField(max_digits=8, decimal_places=2, required=False, 
            widget=forms.TextInput(attrs={'class': 'new-price', 'size': '6', 'value': '0'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    
    def __init__(self, community, *args, **kwargs):
        super(FunctionResourceTypeForm, self).__init__(*args, **kwargs)
        self.fields["resource_type"].choices = [('', '----------')] + [
            (cr.resource_type.id, cr.resource_type.name) for cr in community.resources.all()
        ]
        
    class Meta:
        model = FunctionResourceType
        fields = ('resource_type', 'role', 'quantity', 'price')

        
class FunctionResourceFlowForm(forms.ModelForm):
    quantity = forms.IntegerField(required=False, widget=forms.TextInput(
            attrs={'class': 'quantity', 'size': '6', 'value': '1'}))
    price = forms.DecimalField(max_digits=8, decimal_places=2, required=False, 
            widget=forms.TextInput(attrs={'class': 'new-price', 'size': '6', 'value': '0'}))

        
    class Meta:
        model = FunctionResourceFlow
        exclude = ('value',)
        
        
class AgentResourceFlowForm(forms.ModelForm):
    quantity = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '6', 'value': '1'}))
    price = forms.DecimalField(max_digits=8, decimal_places=2, required=False, 
            widget=forms.TextInput(attrs={'size': '6', 'value': '0'}))
        
    class Meta:
        model = AgentResourceFlow
        exclude = ('value',)
        
        
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
    aspect = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '32', 'class': 'function-aspect'}))


class AgentFunctionForm(forms.ModelForm):
    aspect = forms.CharField(required=False)
    
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
    auto_names = forms.CharField(required=False, widget=forms.HiddenInput)
    name = forms.CharField(widget=forms.TextInput(attrs={'size': '24', 'class': 'resource-name'}))
    quantity = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': '7', 'value': '1'}))
    price = forms.DecimalField(max_digits=8, decimal_places=2, required=False, 
            widget=forms.TextInput(attrs={'class': 'new-price', 'size': '7', 'value': '0'}))
    
    def __init__(self, function_resource=None, *args, **kwargs):
        super(AgentFunctionResourceForm, self).__init__(*args, **kwargs)
        if function_resource:
            self.fields["role"].choices = [(function_resource.role, function_resource.role)]
    
    class Meta:
        model = AgentFunctionResourceType
        fields = ('role', 'quantity', 'price')

        
class EmailForm(forms.Form):
    email_address = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField(widget = forms.Textarea)
    
    
TOGGLE_CHOICES = (
    ('qty', 'Quantity or'),
    ('price', 'Price or'),
    ('val', 'Value'),
) 

class QuantityPriceValueForm(forms.Form):
    toggle = forms.ChoiceField(choices=TOGGLE_CHOICES, widget=forms.RadioSelect(attrs={'class': 'tog'}))
    
LESS_TOGGLE_CHOICES = (
    ('qty', 'Quantity or'),
    ('val', 'Value'),
) 

class QuantityValueForm(forms.Form):
    toggle = forms.ChoiceField(choices=LESS_TOGGLE_CHOICES, widget=forms.RadioSelect(attrs={'class': 'tog'}))
    
LEVEL_CHOICES = (
    ('fn', 'Functions or'),
    ('agt', 'Agents or'),
    ('grp', 'Groups'),
) 

class FunctionAgentLevelForm(forms.Form):
    level = forms.ChoiceField(choices=LEVEL_CHOICES, widget=forms.RadioSelect(attrs={'class': 'tog'}))


TWO_LEVEL_CHOICES = (
    ('fn', 'Functions or'),
    ('agt', 'Agents'),
) 

class FunctionAgentTwoLevelForm(forms.Form):
    level = forms.ChoiceField(choices=TWO_LEVEL_CHOICES, widget=forms.RadioSelect(attrs={'class': 'tog'}))



class AgentAreaForm(forms.Form):
    location = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'tog'}))

    def __init__(self, community, *args, **kwargs):
        super(AgentAreaForm, self).__init__(*args, **kwargs)
        self.fields["location"].choices = [
            ('agt', 'Agent or'),('area', community.agent_geographic_area_name)]

        
class ValueAddedSelectionForm(forms.Form):
    starting_function = forms.ChoiceField()
    resource_name_contains = forms.CharField(required=False)
    resource_aspect = forms.ChoiceField(required=False)
    
    def __init__(self, cluster, *args, **kwargs):
        super(ValueAddedSelectionForm, self).__init__(*args, **kwargs)
        self.fields["starting_function"].choices = [
            (fun.id, fun.name) for fun in cluster.functions.all()]
        #import pdb; pdb.set_trace()
        community = cluster.community
        if community.resource_aspect_name:
            crs = cluster.community_resources()
            aspects = [cr.aspect for cr in crs]
            aspects = list(set(aspects))
            if aspects:
                self.fields["resource_aspect"].choices = [('', '----------')] + [
                    (aspect, aspect) for aspect in aspects]


class CommunityMemberForm(forms.ModelForm):
    #id = forms.CharField(widget=forms.HiddenInput)
    community = forms.ModelChoiceField(
        queryset=Community.objects.all(),
        widget=forms.HiddenInput)
    member = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.HiddenInput)
    
    class Meta:
        model = CommunityMember

        
class CommunityMemberCreationForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-xlarge',}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-xlarge',}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'input-xxlarge',}))
    permission_role = forms.ChoiceField(label="Role", choices=PERMISSION_ROLE_CHOICES,)

    class Meta:
        model = CommunityMember
        exclude = ("community", "member")
        
    def __init__(self, *args, **kwargs):
        super(CommunityMemberCreationForm, self).__init__(*args, **kwargs)    
        field_order = ["first_name", "last_name", "email", "permission_role"]
        if not OrderedDict or hasattr(self.fields, "keyOrder"):
            self.fields.keyOrder = field_order
        else:
            self.fields = OrderedDict((k, self.fields[k]) for k in field_order)
