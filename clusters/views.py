from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Q
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.core.mail import send_mail
from django.core import serializers

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


class FlowResource(object):
     def __init__(self, resource_type):
         self.resource_type = resource_type

# does not work; FlowResource objects cannot fake it for FunctionResourceTypes
def flow_radial_graph_params(cluster):
    template_params = {}
    flows = FunctionResourceFlow.objects.filter(
        from_function__cluster=cluster)
    functions = []
    resources = []
    edges = []
    for flow in flows:
        from_fn = flow.from_function
        try:
            len(from_fn.inputs)
        except TypeError:
            from_fn.inputs = []
        from_fn.inputs.append(FlowResource(flow.resource_type))
        to_fn = flow.to_function
        try:
            len(from_fn.outputs)
        except TypeError:
            to_fn.outputs = []
        to_fn.outputs.append(FlowResource(flow.resource_type))
        functions.extend([from_fn, to_fn])
        resources.append(flow.resource_type)
    functions = list(set(functions))
    resources = list(set(resources))
    
    agents = {}
    for ef in functions:
        for agent in ef.agents.all():
            #agents.setdefault(ef.node_id(), []).append(agent.agent.name)
            agents.setdefault(ef, []).append(agent.agent)
            
    root = cluster.root()
                       
    template_params =  {
        "cluster": cluster,
        "functions": functions,
        "resources": resources,
        "function_agents": agents,
        "root": root,
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
    
    #import pdb; pdb.set_trace()
    
    agents = cluster.agents()
    for agent in agents:
        agent.cluster_functions = agent.functions.filter(function__cluster=cluster)
        for cf in agent.cluster_functions:
            cf.resources = cf.function.resources.all()
            for res in cf.resources:
                res.agent_resource_list = res.resources_for_agent(agent)
    
    return render_to_response("clusters/cluster_agents.html", {
        "cluster": cluster,
        "agents": agents,
        "map_url": cluster.map_url,
        }, context_instance=RequestContext(request))
    
    
@login_required
def edit_cluster_functions(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    
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
    template_params = network_params(cluster)
    template_params["functions"] = functions
    template_params["resources"] = resources
    template_params["new_function_form"] = new_function_form
    template_params["new_resource_form"] = new_resource_form
    template_params["resource_names"] = resource_names
    return render_to_response("clusters/edit_cluster_functions.html", 
        #"cluster": cluster,
        #"functions": functions,
        #"resources": resources,
        #"new_function_form": new_function_form,
        #"new_resource_form": new_resource_form,
        #"resource_names": resource_names,
        template_params,
        context_instance=RequestContext(request))
    
@login_required
def edit_flows(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    
    new_function_form = EconomicFunctionForm(prefix="function")
    new_resource_form = EconomicResourceTypeForm(prefix="resource")
    
    flows = FunctionResourceFlow.objects.filter(
        from_function__cluster=cluster)
    
    FlowFormSet = modelformset_factory(
        FunctionResourceFlow,
        form=FunctionResourceFlowForm,
        can_delete=True,
        extra=3,
        )
    formset = FlowFormSet(
        queryset=FunctionResourceFlow.objects.filter(
            from_function__cluster=cluster),
        data=request.POST or None,
        )
    function_choices = [('', '----------')] + [
            (fn.id, fn.name) for fn in cluster.functions.all()
            ]
    resource_choices = [('', '----------')] + [
            (cr.resource_type.id, cr.resource_type.name) for cr in cluster.community.resources.all()
            ]
    for form in formset.forms:
        form.fields['from_function'].choices = function_choices
        form.fields['to_function'].choices = function_choices
        form.fields['resource_type'].choices = resource_choices
        
    resource_names = ';'.join([res.name for res in EconomicResourceType.objects.all()])
    
    if request.method == "POST":
        #import pdb; pdb.set_trace()
        for form in formset.forms:
            if form.is_valid():
                delete = form.cleaned_data["DELETE"]
                if delete:
                    #todo: this delete code is odd.
                    #First, I expected formsets to delete automatically id DELETE is True.
                    #Second, returning an object when requesting id is nice
                    #but smells like it might break in the future.
                    #import pdb; pdb.set_trace()
                    deleted = form.cleaned_data["id"]
                    deleted.delete()
                else:
                    form.save()
        return HttpResponseRedirect('/%s/%s/'
               % ('clusters/editflows', cluster.id))
    
    template_params = flow_params(cluster)
    template_params["new_function_form"] = new_function_form
    template_params["new_resource_form"] = new_resource_form
    template_params["resource_names"] = resource_names
    template_params["formset"] = formset
    return render_to_response("clusters/edit_flows.html",
        template_params,
        context_instance=RequestContext(request))
    
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
   
class Edge(object):
     def __init__(self, from_node, to_node, amount, width=1):
         self.from_node = from_node
         self.to_node = to_node
         self.amount = amount
         self.width = width


def network_params(cluster):
    template_params = {}
    frts = FunctionResourceType.objects.filter(
        function__cluster=cluster)
    edges = []
    rtypes = []
    total = 0.0
    if frts:
        nodes = list(cluster.functions.all())
        for fn in nodes:
            for v in fn.inputs():
                rtypes.append(v.resource_type)
                total += v.amount
                edges.append(Edge(v.resource_type, fn, v.amount))
            for v in fn.outputs():
                rtypes.append(v.resource_type)
                total += v.amount
                edges.append(Edge(fn, v.resource_type, v.amount))
    else:
        flows = FunctionResourceFlow.objects.filter(
            from_function__cluster=cluster)
        nodes = []
        edges = []
        for flow in flows:
            nodes.extend([flow.from_function, flow.to_function, flow.resource_type])
            total += flow.amount
            edges.append(Edge(flow.from_function, flow.resource_type, flow.amount))
            edges.append(Edge(flow.resource_type, flow.to_function, flow.amount))
        nodes = list(set(nodes))
            
    for edge in edges:
        width = round((edge.amount / total), 2) * 50
        width = int(width)
        edge.width = width
    nodes.extend(list(set(rtypes)))
    template_params =  {
        'cluster': cluster,
        'nodes': nodes,
        'edges': edges,
    }
    return template_params
    

def network(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    template_params = network_params(cluster)
    template_params["use_window_size"] = True
    return render_to_response("clusters/network.html",
        template_params,
        context_instance=RequestContext(request))
    
class FlowEdge(object):
     def __init__(self, from_node, to_node, label, amount, width=1):
         self.from_node = from_node
         self.to_node = to_node
         self.label = label
         self.amount = amount
         self.width = width
         
def flow_params(cluster):
    template_params = {}
    flows = FunctionResourceFlow.objects.filter(
        from_function__cluster=cluster)
    nodes = []
    total = 0.0
    for flow in flows:
        nodes.extend([flow.from_function, flow.to_function])
        total += flow.amount
    nodes = list(set(nodes))
    prev = None
    edges = []
    for flow in flows:
        if prev:
            prev_match = prev.to_function.id==flow.to_function.id and prev.from_function.id==flow.from_function.id
        else:
            prev_match=False
        if prev_match:
            edge.label = ";".join([edge.label, flow.resource_type.name])
            edge.amount += flow.amount
        else:
            edge = FlowEdge(flow.from_function, flow.to_function, flow.resource_type.name, flow.amount)
            edges.append(edge)
        prev = flow                  
    for edge in edges:
        width = round((edge.amount / total), 2) * 50
        width = int(width)
        edge.width = width
    template_params =  {
        'cluster': cluster,
        'nodes': nodes,
        'edges': edges,
    }
    return template_params
    
def flows(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    template_params = flow_params(cluster)
    template_params["use_window_size"] = True
    return render_to_response("clusters/flows.html",
        template_params,
        context_instance=RequestContext(request))    


def iotable(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    iotable = input_output_table(cluster)
    
    return render_to_response("clusters/iotable.html",{ 
        "cluster": cluster,
        "iotable": iotable,
    }, context_instance=RequestContext(request))
    
def diagnostics(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    
    function_production_without_consumption = cluster.function_production_without_consumption()
    function_consumption_without_production = cluster.function_consumption_without_production()
    
    return render_to_response("clusters/diagnostics.html",{ 
        "cluster": cluster,
        "function_production_without_consumption": function_production_without_consumption,
        "function_consumption_without_production": function_consumption_without_production,
    }, context_instance=RequestContext(request))
    
def model_errors(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    
    disjoints = cluster.disjoints()
    missing_function_numbers = cluster.missing_function_numbers()
    missing_agent_numbers = cluster.missing_agent_numbers()
    function_agent_diffs = cluster.function_agent_diffs()
    
    return render_to_response("clusters/model_errors.html",{ 
        "cluster": cluster,
        "disjoints": disjoints,
        "missing_function_numbers": missing_function_numbers,
        "missing_agent_numbers": missing_agent_numbers,
        "function_agent_diffs": function_agent_diffs,
    }, context_instance=RequestContext(request))
    
def economic_functions(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
       
    functions = cluster.functions.all()
        
    resources = cluster.resources()
    for res in resources:
        res.my_consumers = res.cluster_consumers(cluster)
        res.my_producers = res.cluster_producers(cluster)
        
    flows = FunctionResourceFlow.objects.filter(
        from_function__cluster=cluster)
    
    return render_to_response("clusters/economic_functions.html", {
        "cluster": cluster,
        "functions": functions,
        "resources": resources,
        "flows": flows,
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
        next = request.POST.get("next")
        cluster = get_object_or_404(Cluster, pk=cluster_id)
        form = EconomicFunctionForm(request.POST, prefix="function")
        #import pdb; pdb.set_trace()
        if form.is_valid():
            fun = form.save(commit=False)
            fun.cluster = cluster
            fun.save()         
    return HttpResponseRedirect(next)
    
@login_required 
def inline_new_agent_function(request, cluster_id, agent_id):
    if request.method == "POST":
        cluster = get_object_or_404(Cluster, pk=cluster_id)
        agent = get_object_or_404(EconomicAgent, pk=agent_id)
        form = AgentFunctionForm(cluster, agent, data=request.POST, prefix="function")
        #import pdb; pdb.set_trace()
        #print "b4 form validity check"
        if form.is_valid():
            #print "after form validity check"
            fun = form.save(commit=False)
            fun.agent = agent
            fun.save()
        #else:
        #    print "invalid form:", form
            
    return HttpResponseRedirect('/%s/%s/%s/'
        % ('clusters/editclusteragent', cluster_id, agent_id))
    
    
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
    agent_names = '~'.join([agt.name for agt in EconomicAgent.objects.all()])
    if request.method == "POST":
        if form.is_valid():
            data = form.cleaned_data
            name = data['name']
            try:
                agent = EconomicAgent.objects.get(name=name)
            except EconomicAgent.DoesNotExist:
                agent = form.save()
            crt, created = CommunityAgent.objects.get_or_create(community=cluster.community, agent=agent)
            return HttpResponseRedirect('/%s/%s/%s/'
               % ('clusters/editclusteragent', cluster_id, agent.id))
    return render_to_response("clusters/new_cluster_agent.html",{ 
        "cluster": cluster,
        "form": form,
        "agent_names": agent_names,
    }, context_instance=RequestContext(request))
  

@login_required    
def edit_cluster_agent(request, cluster_id, agent_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    agent = get_object_or_404(EconomicAgent, pk=agent_id)
    agent.cluster_functions = agent.functions.filter(function__cluster=cluster)
    for cf in agent.cluster_functions:
        cf.resources = cf.function.resources.all()
        for res in cf.resources:
            res.agent_resource_form = AgentResourceForm(res)
            res.agent_resource_list = res.resources_for_agent(agent)
           
    new_function_form = AgentFunctionForm(cluster, agent, prefix="function")
    
    resource_names = '~'.join([res.name for res in EconomicResourceType.objects.all()])
    
    return render_to_response("clusters/edit_cluster_agent.html",{ 
        "cluster": cluster,
        "agent": agent,
        "new_function_form": new_function_form,
        "resource_names": resource_names,
    }, context_instance=RequestContext(request))
    
    
def json_agent_address(request, agent_name):
    # Note: serializer requires an iterable, not a single object. Thus filter rather than get.  
    data = serializers.serialize("json", EconomicAgent.objects.filter(name=agent_name), fields=('address',))    
    return HttpResponse(data, mimetype="text/json-comment-filtered")

def change_function_resource_amount(request):
    id = request.POST.get("id")
    amount = request.POST.get("amount")
    frt = get_object_or_404(FunctionResourceType, pk=id)
    #import pdb; pdb.set_trace()
    amount = int(amount)
    if amount != frt.amount:
        frt.amount = int(amount)
        frt.save()
    data = "ok"
    return HttpResponse(data, mimetype="text/plain")

def delete_function_resource(request, id):
    frt = get_object_or_404(FunctionResourceType, pk=id)
    cluster = frt.function.cluster
    frt.delete()
    return HttpResponseRedirect('/%s/%s/'
        % ('clusters/editclusterfunctions', cluster.id))

@login_required    
def inline_new_resource(request, cluster_id):
    if request.method == "POST":
        next = request.POST.get("next")
        cluster = get_object_or_404(Cluster, pk=cluster_id)
        form = EconomicResourceTypeForm(request.POST, prefix="resource")
        if form.is_valid():
            data = form.cleaned_data
            name = data['name']
            try:
                resource = EconomicResourceType.objects.get(name=name)
            except EconomicResourceType.DoesNotExist:
                resource = form.save()
            crt, created = CommunityResourceType.objects.get_or_create(community=cluster.community, resource_type=resource)
    return HttpResponseRedirect(next)

@login_required    
def inline_agent_resource(request, cluster_id, agent_id, parent_id):
    if request.method == "POST":
        agent = get_object_or_404(EconomicAgent, pk=agent_id)
        parent = get_object_or_404(EconomicResourceType, pk=parent_id)
        cluster = get_object_or_404(Cluster, pk=cluster_id)
        form = AgentResourceForm(function_resource=None, data=request.POST)
        
        if form.is_valid():
            data = form.cleaned_data
            name = data['name']
            role = data['role']
            amount = data['amount']
            new_resource = True
            
            #import pdb; pdb.set_trace()
            
            try:
                resource = EconomicResourceType.objects.get(name=name)
                if resource.id == parent.id:
                    new_resource = False
                elif resource.parent:
                    if resource.parent.id == parent.id or resource.is_child_of(parent):
                        new_resource = False               
            except EconomicResourceType.DoesNotExist:
                pass
            if new_resource:
                resource = EconomicResourceType(name=name, parent=parent)
                resource.save()
            AgentResourceType(resource_type=resource, agent=agent, role=role, amount=amount).save()
            crt, created = CommunityResourceType.objects.get_or_create(community=cluster.community, resource_type=resource)
    return HttpResponseRedirect('/%s/%s/%s/'
       % ('clusters/editclusteragent', cluster_id, agent.id))


@login_required    
def new_function_resource(request, function_id):
    if request.method == "POST":
        fun = get_object_or_404(EconomicFunction, pk=function_id)
        community = fun.cluster.community
        form = FunctionResourceTypeForm(community=community, data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            fr = form.save(commit=False)
            fr.function = fun
            fr.save()
    return HttpResponseRedirect('/%s/%s/'
        % ('clusters/editclusterfunctions', fun.cluster.id))
        
    
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
