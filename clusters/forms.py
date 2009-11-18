from django import forms

from clusters.models import *
from clusters.fields import *

class EconomicFunctionForm(forms.ModelForm):
    
    class Meta:
        model = EconomicFunction
        fields = ('name',)
        
        
class FunctionResourceTypeForm(forms.ModelForm):
    resource_type = ResourceChoiceField(EconomicResourceType.objects.all())
    
#    def __init__(self, community, *args, **kwargs):
#        super(FunctionResourceTypeForm, self).__init__(*args, **kwargs)
#        rtypes = CommunityResourceType.objects.filter(community=community)
#        self.fields["resource_type"].choices = [('', '----------')] + [(rt.resource_type.id, rt.resource_type.name) for rt in rtypes]
    
    class Meta:
        model = FunctionResourceType
        fields = ('resource_type', 'role', 'amount')


#from pbc.views:
#    product_choices = [(prod.id, prod.long_name) for prod in product_list]
#    product_choices = [(prod.id, prod.long_name) for prod in product_list]
#    for form in formset.forms:
#        form.fields['product'].choices = product_choices
        

        
class EmailForm(forms.Form):
    email_address = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField(widget = forms.Textarea)
    