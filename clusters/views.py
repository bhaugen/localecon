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
    #template_params = cluster_params(cluster)
    
    
    return render_to_response("clusters/cluster.html", {
        "cluster": cluster,
        "map_url": cluster.map_url,
        #template_params,
        }, context_instance=RequestContext(request))
    
def cluster_agents(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    
    agents = cluster.agents()
    for agent in agents:
        agent.cluster_functions = agent.functions.filter(function__cluster=cluster)
        for cf in agent.cluster_functions:
            cf.resources = cf.function.resources.all()
    
    return render_to_response("clusters/cluster_agents.html", {
        "cluster": cluster,
        "agents": agents,
        "map_url": cluster.map_url,
        }, context_instance=RequestContext(request))
    
    
@login_required
def edit_cluster_functions(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    #template_params = cluster_params(cluster)
    
    new_function_form = EconomicFunctionForm(prefix="function")
    new_resource_form = EconomicResourceTypeForm(prefix="resource")
    
    functions = cluster.functions.all()
    for fun in functions:
        fun.form = FunctionResourceTypeForm(community=cluster.community)
        
    resources = cluster.resources()
    for res in resources:
        res.my_consumers = res.cluster_consumers(cluster)
        res.my_producers = res.cluster_producers(cluster)
        
    resource_names = ';'.join([res.name for res in EconomicResourceType.objects.all()])
    
    return render_to_response("clusters/edit_cluster_functions.html", {
        "cluster": cluster,
        "functions": functions,
        "resources": resources,
        "new_function_form": new_function_form,
        "new_resource_form": new_resource_form,
        "resource_names": resource_names,
        #template_params,
        }, context_instance=RequestContext(request))
    
def featured_cluster(request):
    cluster = get_featured_cluster()
    template_params = {}
    if cluster:
        template_params = cluster_params(cluster)
    
    return render_to_response("clusters/featured_cluster.html", 
        template_params,
        context_instance=RequestContext(request))
    
def radial_graph(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    template_params = cluster_params(cluster)
    
    return render_to_response("clusters/radial_graph.html", 
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

@login_required    
def new_function(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    function_form = EconomicFunctionForm()
    
    ResourceFormSet = formset_factory(FunctionResourceTypeFormX, extra=5)
    resource_formset = ResourceFormSet()
    rtypes = CommunityResourceType.objects.filter(community=cluster.community)
    for form in resource_formset.forms:
        #form.fields['resource_type'].choices = [('', '----------')] + [(rt.resource_type.id, rt.resource_type.name) for rt in rtypes]
        form.fields['resource_type'].widget.set_local_choices([('', '----------')] + [(rt.resource_type.id, rt.resource_type.name) for rt in rtypes])
    
    #import pdb; pdb.set_trace()
        
    AgentFormSet = formset_factory(FunctionAgentForm, extra=5)
    agent_formset = AgentFormSet()
    agents = CommunityAgent.objects.filter(community=cluster.community)
    for form in agent_formset.forms:
        form.fields['agent'].choices = [('', '----------')] + [(agt.agent.id, agt.agent.name) for agt in agents]
        #form.fields['agent'].widget.set_local_choices([('', '----------')] + [(agt.agent.id, agt.agent.name) for agt in agents])
        
    return render_to_response("clusters/new_function.html",{ 
        "cluster": cluster,
        "function_form": function_form,
        "resource_formset": resource_formset,
        "agent_formset": agent_formset,
    }, context_instance=RequestContext(request))
   
@login_required 
def inline_new_function(request, cluster_id):
    if request.method == "POST":
        cluster = get_object_or_404(Cluster, pk=cluster_id)
        form = EconomicFunctionForm(request.POST)
        if form.is_valid():
            fun = form.save(commit=False)
            fun.cluster = cluster
            fun.save()
            
    return HttpResponseRedirect('/%s/%s/'
        % ('clusters/editcluster', cluster_id))
    
    
@login_required    
def new_resource(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    form = EconomicResourceTypeFormX(data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            data = form.cleaned_data
            name = data['name']
            try:
                resource = EconomicResourceType.objects.get(name=name)
            except EconomicResourceType.DoesNotExist:
                pass
                #resource = form.save()
            #crt, created = CommunityResourceType.objects.get_or_create(community=cluster.community, resource_type=resource)
    return render_to_response("clusters/new_resource.html",{ 
        "form": form,
    }, context_instance=RequestContext(request))
    
@login_required    
def new_cluster_agent(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    form = EconomicAgentForm(data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            data = form.cleaned_data
            name = data['name']
            try:
                agent = EconomicAgent.objects.get(name=name)
            except EconomicResourceType.DoesNotExist:
                pass
                #agent = form.save()
            #crt, created = CommunityAgent.objects.get_or_create(community=cluster.community, agent=agent)
    return render_to_response("clusters/new_resource.html",{ 
        "form": form,
    }, context_instance=RequestContext(request))
    
@login_required    
def inline_new_resource(request, cluster_id):
    if request.method == "POST":
        cluster = get_object_or_404(Cluster, pk=cluster_id)
        form = EconomicResourceTypeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            name = data['name']
            try:
                resource = EconomicResourceType.objects.get(name=name)
            except EconomicResourceType.DoesNotExist:
                resource = form.save()
            crt, created = CommunityResourceType.objects.get_or_create(community=cluster.community, resource_type=resource)
    return HttpResponseRedirect('/%s/%s/'
        % ('clusters/editcluster', cluster_id))

@login_required    
def new_function_resource(request, function_id):
    if request.method == "POST":
        fun = get_object_or_404(EconomicFunction, pk=function_id)
        form = FunctionResourceTypeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            fr = form.save(commit=False)
            fr.function = fun
            fr.save()
    return HttpResponseRedirect('/%s/%s/'
        % ('clusters/editcluster', fun.cluster.id))
        
    
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