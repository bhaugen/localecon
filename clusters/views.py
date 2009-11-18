from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Q
from django.forms.formsets import formset_factory
from django.core.mail import send_mail

from datetime import datetime, timedelta

from clusters.models import *
from clusters.forms import *

def cluster_params(cluster):
    template_params = {}
    linked_efs = []
    resources = []
    efs = EconomicFunction.objects.filter(cluster=cluster)  
    for ef in efs:
        inputs = ef.inputs()
        if inputs:
            linked_efs.append(ef)
            for inp in inputs:
                resources.append(inp.resource_type)
        outputs = ef.outputs()
        if outputs:
            linked_efs.append(ef)
            for output in outputs:
                resources.append(output.resource_type)
                
    efs = list(set(linked_efs))
    resources = list(set(resources))
    
    agents = {}
    for ef in efs:
        for agent in ef.agents.all():
            #agents.setdefault(ef.node_id(), []).append(agent.agent.name)
            agents.setdefault(ef, []).append(agent.agent)
            
    root = cluster.root()
    
    frtable = function_resource_table(cluster)
                       
    template_params =  {
        "cluster": cluster,
        "functions": efs,
        "resources": resources,
        "function_agents": agents,
        "root": root,
        "frtable": frtable,
    }
    return template_params
    
def clusters(request):
    communities = Community.objects.all()
    
    return render_to_response("clusters/clusters.html", {
        "communities": communities,
    }, context_instance=RequestContext(request))

  
def cluster(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    template_params = cluster_params(cluster)
    
    return render_to_response("clusters/cluster.html", 
        template_params,
        context_instance=RequestContext(request))
    
def featured_cluster(request):
    cluster_id = 3
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    template_params = cluster_params(cluster)
    
    return render_to_response("clusters/featured_cluster.html", 
        template_params,
        context_instance=RequestContext(request))

def iotable(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    iotable = input_output_table(cluster)
    
    return render_to_response("clusters/iotable.html",{ 
        "cluster": cluster,
        "iotable": iotable,
    }, context_instance=RequestContext(request))
    
def economic_functions(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    
    return render_to_response("clusters/economic_functions.html",{ 
        "cluster": cluster,
    }, context_instance=RequestContext(request))
    
def economic_function(request, function_id):
    ef = get_object_or_404(EconomicFunction, pk=function_id)
    
    return render_to_response("clusters/economic_functions.html",{ 
        "economic_function": ef,
    }, context_instance=RequestContext(request))
    
def new_function(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    
    return render_to_response("clusters/new_function.html",{ 
        "cluster": cluster,
    }, context_instance=RequestContext(request))
    
def fr_table(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    frtable = function_resource_table(cluster)
    
    return render_to_response("clusters/fr_table.html",{ 
        "cluster": cluster,
        "frtable": frtable,
    }, context_instance=RequestContext(request))
    
def send_email(request):
    if request.method == "POST":
        email_form = EmailForm(request.POST)
        if email_form.is_valid():
            data = email_form.cleaned_data
            from_email = data["email_address"]
            subject = " ".join(["[locecon]", data["subject"]])
            message = data["message"]
            send_mail(subject, message, from_email, ["bob.haugen@gmail.com",])      
            return HttpResponseRedirect(reverse("email_sent"))
    else:
        email_form = EmailForm()
    
    return render_to_response("clusters/send_email.html", {
        "email_form": email_form,
    })