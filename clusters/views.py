from django.shortcuts import render_to_response, get_object_or_404, redirect
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
from django.conf import settings

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
    
    frtable = function_resource_table(cluster, "qty")
                       
    template_params =  {
        "cluster": cluster,
        "functions": efs,
        "resources": resources,
        "function_agents": agents,
        "root": root,
        "frtable": frtable,
    }
    return template_params

def explore_params(cluster):
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
            agents.setdefault(ef, []).append(agent.agent)
            
    root = cluster.root()
                          
    template_params =  {
        "cluster": cluster,
        "functions": efs,
        "resources": resources,
        "function_agents": agents,
        "root": root,
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

  
def cluster(request, cluster_id, location="agt"):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    community = cluster.community
    location_form = None
    if community.agent_geographic_area_name:
        init = {"location": location,}
        location_form = AgentAreaForm(community=community, initial=init, data=request.POST or None)
    if request.method == "POST":
        if location_form:
            if location_form.is_valid():
                location = location_form.cleaned_data["location"]
        return HttpResponseRedirect('/%s/%s/%s/'
                    % ('clusters/cluster', cluster_id, location))
    if location == "agt":
        agents = cluster.agents()
        for agent in agents:
            agent.all_functions = agent.functions.filter(
                function__cluster=cluster)
    else:
        agents = cluster.regions()
    map_center = ",".join([str(community.latitude), str(community.longitude)])
    map_key = settings.GOOGLE_API_KEY   
    return render_to_response("clusters/cluster.html", {
        "cluster": cluster,
        "agents": agents,
        "map_center": map_center,
        "map_key": map_key,
        "zoom_level": community.map_zoom_level,
        "location_form": location_form,
        }, context_instance=RequestContext(request))
    
def cluster_agents(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    
    #import pdb; pdb.set_trace()
    
    agents = cluster.agents()
    for agent in agents:
        agent.cluster_functions = agent.functions.filter(function__cluster=cluster)
        for cf in agent.cluster_functions:
            cf.rsrcs = cf.function.resources.all()
            if cf.rsrcs:
                for res in cf.rsrcs:
                    res.agent_resource_list = res.function_resources_for_agent(agent)
            else:
                cf.agent_resources = cf.function_resources.all()
            outliers = []
            candidates = cf.function_resources.all()
            for c in candidates:
                if c.is_outlier():
                    outliers.append(c)
                    cf.outliers = outliers
    #import pdb; pdb.set_trace()
    return render_to_response("clusters/cluster_agents.html", {
        "cluster": cluster,
        "agents": agents,
        }, context_instance=RequestContext(request))
    
    
@login_required
def edit_cluster_functions(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    community = cluster.community
    symbol = "$"
    try:
        symbol = community.unit_of_value.symbol
    except:
        pass
    new_function_form = EconomicFunctionForm(prefix="function")
    new_resource_form = EconomicResourceTypeForm(prefix="resource")
    
    functions = cluster.functions.all()
    for fun in functions:
        fun.form = FunctionResourceTypeForm(community=cluster.community)
        
    resources = cluster.resources()
    for res in resources:
        res.my_consumers = res.cluster_consumers(cluster)
        res.my_producers = res.cluster_producers(cluster)
       
    used = [cr.resource_type.id for cr in community.resources.all()]
    resource_names = ';'.join([
        res.name for res in EconomicResourceType.objects.all().exclude(id__in=used)])
    template_params = network_params(cluster, "qty")
    template_params["symbol"] = symbol
    template_params["functions"] = functions
    template_params["resources"] = resources
    template_params["new_function_form"] = new_function_form
    template_params["new_resource_form"] = new_resource_form
    template_params["resource_names"] = resource_names
    function_aspect_name = cluster.function_aspect_name
    resource_aspect_name = cluster.community.resource_aspect_name
    template_params["function_aspect_name"] = function_aspect_name
    template_params["resource_aspect_name"] = resource_aspect_name
    return render_to_response("clusters/edit_cluster_functions.html", 
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
        
    used = [cr.resource_type.id for cr in cluster.community.resources.all()]
    resource_names = ';'.join([
        res.name for res in EconomicResourceType.objects.all().exclude(id__in=used)])
    
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
    
    template_params = flow_params(cluster, "qty")
    template_params["new_function_form"] = new_function_form
    template_params["new_resource_form"] = new_resource_form
    template_params["resource_names"] = resource_names
    function_aspect_name = cluster.function_aspect_name
    resource_aspect_name = cluster.community.resource_aspect_name
    template_params["function_aspect_name"] = function_aspect_name
    template_params["resource_aspect_name"] = resource_aspect_name
    template_params["formset"] = formset
    return render_to_response("clusters/edit_flows.html",
        template_params,
        context_instance=RequestContext(request))

@login_required
def edit_agent_flows(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    
    new_function_form = InlineAgentFunctionForm(cluster=cluster, prefix="function")
    new_resource_form = EconomicResourceTypeForm(prefix="resource")
    
    flows = list(AgentResourceFlow.objects.filter(
        from_function__function__cluster=cluster))
    flows.extend(list(AgentResourceFlow.objects.filter(
        to_function__function__cluster=cluster)))
    
    FlowFormSet = modelformset_factory(
        AgentResourceFlow,
        form=AgentResourceFlowForm,
        can_delete=True,
        extra=3,
        )
    formset = FlowFormSet(
        queryset=AgentResourceFlow.objects.filter(
            from_function__function__cluster=cluster),
        data=request.POST or None,
        )
    agent_functions = AgentFunction.objects.filter(
        function__cluster=cluster)
    function_choices = [('', '----------')] + [
            (fn.id, fn) for fn in agent_functions]
    resources = cluster.community.resources.all()
    resource_choices = [('', '----------')] + [
            (cr.resource_type.id, cr.resource_type.name) for cr in resources
            ]
    for form in formset.forms:
        form.fields['from_function'].choices = function_choices
        form.fields['to_function'].choices = function_choices
        form.fields['resource_type'].choices = resource_choices
    
    used = [cr.resource_type.id for cr in resources]
    erts = EconomicResourceType.objects.all().exclude(id__in=used)    
    resource_names = '~'.join([res.name for res in erts])
    function_names = '~'.join([fn.name for fn in cluster.functions.all()])
    
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
               % ('clusters/editagentflows', cluster.id))
    
    template_params = agent_flow_params(cluster, "qty")
    template_params["new_function_form"] = new_function_form
    template_params["new_resource_form"] = new_resource_form
    template_params["resource_names"] = resource_names
    template_params["function_names"] = function_names
    function_aspect_name = cluster.function_aspect_name
    resource_aspect_name = cluster.community.resource_aspect_name
    template_params["function_aspect_name"] = function_aspect_name
    template_params["resource_aspect_name"] = resource_aspect_name
    template_params["formset"] = formset
    return render_to_response("clusters/edit_agent_flows.html",
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
    
def splitthousands(n, sep=','):
    s = str(n)
    if len(s) <= 3: return s  
    return splitthousands(s[:-3], sep) + sep + s[-3:]
   
class Edge(object):
     def __init__(self, from_node, to_node, quantity, label, width=1):
         self.from_node = from_node
         self.to_node = to_node
         self.quantity = quantity
         self.label = label
         self.width = width

def agent_network_params(cluster, toggle):
    template_params = {}
    frts = AgentFunctionResourceType.objects.filter(
        agent_function__function__cluster=cluster)
    symbol = "$"
    if toggle == "val" or toggle == "price":
        try:
            symbol = cluster.community.unit_of_value.symbol
        except:
            pass
    edges = []
    rtypes = []
    if toggle == "price":
        total = Decimal("0.00")
    else:
        total = 0.0
    if frts:
        nodes = list(cluster.agents())
        for agt in nodes:
            for v in agt.function_inputs(cluster):
                rtypes.append(v.resource_type)
                if toggle == "val":
                    value = v.get_value()
                    total += value
                    val_string = "".join([symbol, splitthousands(value)])
                    edges.append(Edge(v.resource_type, agt, value, val_string))
                elif toggle == "price":
                    total += v.price
                    p_string = "".join([symbol, str(v.price.quantize(Decimal(".01")))])
                    edges.append(Edge(v.resource_type, agt, v.price, p_string))
                else:
                    total += v.quantity
                    qty_string = splitthousands(v.quantity)
                    edges.append(Edge(v.resource_type, agt, v.quantity, qty_string))
            for v in agt.function_outputs(cluster):
                rtypes.append(v.resource_type)
                if toggle == "val":
                    value = v.get_value()
                    total += value
                    val_string = "".join([symbol, splitthousands(value)])
                    edges.append(Edge(agt, v.resource_type, value, val_string))
                elif toggle == "price":
                    total += v.price
                    p_string = "".join([symbol, str(v.price.quantize(Decimal(".01")))])
                    edges.append(Edge(agt, v.resource_type, v.price, p_string))
                else:
                    total += v.quantity
                    qty_string = splitthousands(v.quantity)
                    edges.append(Edge(agt, v.resource_type, v.quantity, qty_string))
    else:
        flows = AgentResourceFlow.objects.filter(
            from_function__function__cluster=cluster)
        nodes = []
        edges = []
        for flow in flows:
            nodes.extend([flow.from_function, flow.to_function, flow.resource_type])
            if toggle == "val":
                value = flow.get_value()
                total += value
                val_string = "".join([symbol, splitthousands(value)])
                edges.append(Edge(flow.from_function, flow.resource_type, value, val_string))
                edges.append(Edge(flow.resource_type, flow.to_function, value, val_string))
            elif toggle == "price":
                total += v.price
                p_string = "".join([symbol, str(v.price.quantize(Decimal(".01")))])
                edges.append(Edge(flow.from_function, flow.resource_type, v.price, p_string))
                edges.append(Edge(flow.resource_type, flow.to_function, v.price, p_string))
            else:
                total += flow.quantity
                qty_string = splitthousands(v.quantity)
                edges.append(Edge(flow.from_function, flow.resource_type, flow.quantity, qty_string))
                edges.append(Edge(flow.resource_type, flow.to_function, flow.quantity, qty_string))
        nodes = list(set(nodes))
            
    for edge in edges:
        width = 1
        if total > 0:
            width = round((edge.quantity / total), 2) * 50
            width = int(width)
            #print "edge.quantity:", edge.quantity, "Width:", width
        edge.width = width
    nodes.extend(list(set(rtypes)))
    template_params =  {
        'cluster': cluster,
        'nodes': nodes,
        'edges': edges,
    }
    return template_params

def group_network_params(cluster, toggle):
    template_params = {}
    groups = cluster.groups()
    symbol = "$"
    if toggle == "val" or toggle == "price":
        try:
            symbol = cluster.community.unit_of_value.symbol
        except:
            pass
    nodes = []
    edges = []
    rtypes = []
    if toggle == "price":
        total = Decimal("0.00")
    else:
        total = 0.0
    if groups:
        nodes = groups
        for agt in nodes:
            for v in agt.function_inputs():
                rtypes.append(v.resource_type)
                if toggle == "val":
                    value = v.get_value()
                    total += value
                    val_string = "".join([symbol, splitthousands(value)])
                    edges.append(Edge(v.resource_type, agt, value, val_string))
                elif toggle == "price":
                    total += v.price
                    p_string = "".join([symbol, str(v.price.quantize(Decimal(".01")))])
                    edges.append(Edge(v.resource_type, agt, v.price, p_string))
                else:
                    total += v.quantity
                    qty_string = splitthousands(v.quantity)
                    edges.append(Edge(v.resource_type, agt, v.quantity, qty_string))
            for v in agt.function_outputs():
                rtypes.append(v.resource_type)
                if toggle == "val":
                    value = v.get_value()
                    total += value
                    val_string = "".join([symbol, splitthousands(value)])
                    edges.append(Edge(agt, v.resource_type, value, val_string))
                elif toggle == "price":
                    total += v.price
                    p_string = "".join([symbol, str(v.price.quantize(Decimal(".01")))])
                    edges.append(Edge(agt, v.resource_type, v.price, p_string))
                else:
                    total += v.quantity
                    qty_string = splitthousands(v.quantity)
                    edges.append(Edge(agt, v.resource_type, v.quantity, qty_string))
            
    for edge in edges:
        width = 1
        if total > 0:
            width = round((edge.quantity / total), 2) * 50
            width = int(width)
        edge.width = width
    nodes.extend(list(set(rtypes)))
    template_params =  {
        'cluster': cluster,
        'nodes': nodes,
        'edges': edges,
    }
    return template_params

def network_params(cluster, toggle):
    template_params = {}
    frts = FunctionResourceType.objects.filter(
        function__cluster=cluster)
    symbol = "$"
    if toggle == "val" or toggle == "price":
        try:
            symbol = cluster.community.unit_of_value.symbol
        except:
            pass
    edges = []
    rtypes = []
    if toggle == "price":
        total = Decimal("0.00")
    else:
        total = 0.0
    if frts:
        nodes = list(cluster.functions.all())
        for fn in nodes:
            for v in fn.inputs():
                rtypes.append(v.resource_type)
                if toggle == "val":
                    value = v.get_value()
                    total += value
                    val_string = "".join([symbol, splitthousands(value)])
                    edges.append(Edge(v.resource_type, fn, value, val_string))
                elif toggle == "price":
                    total += v.price
                    p_string = "".join([symbol, str(v.price.quantize(Decimal(".01")))])
                    edges.append(Edge(v.resource_type, fn, v.price, p_string))
                else:
                    total += v.quantity
                    qty_string = splitthousands(v.quantity)
                    edges.append(Edge(v.resource_type, fn, v.quantity, qty_string))
            for v in fn.outputs():
                rtypes.append(v.resource_type)
                if toggle == "val":
                    value = v.get_value()
                    total += value
                    val_string = "".join([symbol, splitthousands(value)])
                    edges.append(Edge(fn, v.resource_type, value, val_string))
                elif toggle == "price":
                    total += v.price
                    p_string = "".join([symbol, str(v.price.quantize(Decimal(".01")))])
                    edges.append(Edge(v.resource_type, fn, v.price, p_string))
                else:
                    total += v.quantity
                    qty_string = splitthousands(v.quantity)
                    edges.append(Edge(fn, v.resource_type, v.quantity, qty_string))
    else:
        flows = FunctionResourceFlow.objects.filter(
            from_function__cluster=cluster)
        nodes = []
        edges = []
        for flow in flows:
            nodes.extend([flow.from_function, flow.to_function, flow.resource_type])
            if toggle == "val":
                value = flow.get_value()
                total += value
                val_string = "".join([symbol, splitthousands(value)])
                edges.append(Edge(flow.from_function, flow.resource_type, value, val_string))
                edges.append(Edge(flow.resource_type, flow.to_function, value, val_string))
            elif toggle == "price":
                total += v.price
                p_string = "".join([symbol, str(v.price.quantize(Decimal(".01")))])
                edges.append(Edge(flow.from_function, flow.resource_type, v.price, p_string))
                edges.append(Edge(flow.resource_type, flow.to_function, v.price, p_string))
            else:
                total += flow.quantity
                qty_string = splitthousands(flow.quantity)
                edges.append(Edge(flow.from_function, flow.resource_type, flow.quantity, qty_string))
                edges.append(Edge(flow.resource_type, flow.to_function, flow.quantity, qty_string))
        nodes = list(set(nodes))
            
    for edge in edges:
        width = 1
        if total > 0:
            width = round((edge.quantity / total), 2) * 50
            width = int(width)
        edge.width = width
    nodes.extend(list(set(rtypes)))
    template_params =  {
        'cluster': cluster,
        'nodes': nodes,
        'edges': edges,
    }
    return template_params
    

def network(request, cluster_id, toggle="qty", level="fn"):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    toggle_form = QuantityPriceValueForm(
        initial={"toggle": toggle,},
        data=request.POST or None)
    level_form = None
    #import pdb; pdb.set_trace()
    if cluster.agents():
        level_form = FunctionAgentLevelForm(
            initial={"level": level,},
            data=request.POST or None)
    if request.method == "POST":
        if level_form:
            if level_form.is_valid():
                level = level_form.cleaned_data["level"]
        if toggle_form.is_valid():
            toggle = toggle_form.cleaned_data["toggle"]
        return HttpResponseRedirect('/%s/%s/%s/%s/'
                    % ('clusters/network', cluster_id, toggle, level))
    if level == "agt":
        template_params = agent_network_params(cluster, toggle)
    elif level == "grp":
        template_params = group_network_params(cluster, toggle)
    else:
        template_params = network_params(cluster, toggle)
    template_params["use_window_size"] = True
    template_params["toggle_form"] = toggle_form
    template_params["level_form"] = level_form
    #if request.method == "POST":
    #    if level_form:
    #        if level_form.is_valid():
    #            level = level_form.cleaned_data["level"]
    #    else:
    #        if toggle_form.is_valid():
    #            toggle = toggle_form.cleaned_data["toggle"]
    #    return HttpResponseRedirect('/%s/%s/%s/%s/'
    #                % ('clusters/network', cluster_id, toggle, level))
    return render_to_response("clusters/network.html",
        template_params,
        context_instance=RequestContext(request))
    
class FlowEdge(object):
     def __init__(self, from_node, to_node, label, quantity, width=1):
         self.from_node = from_node
         self.to_node = to_node
         self.label = label
         self.quantity = quantity
         self.width = width
         
def group_flow_params(cluster, toggle):
    template_params = {}
    flows = cluster.group_flows()
    nodes = []
    if toggle == "price":
        total = Decimal("0.00")
    else:
        total = 0.0
    for flow in flows:
        nodes.extend([flow.from_function, flow.to_function])
        if toggle == "val":
            total += flow.get_value()
        elif toggle == "price":
            total += flow.price
        else:
            total += flow.quantity
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
            if toggle == "val":
                edge.quantity += flow.get_value()
            elif toggle == "price":
                edge.quantity += flow.price
            else:
                edge.quantity += flow.quantity
        else:
            if toggle == "val":
                nbr = flow.get_value()
            elif toggle == "price":
                nbr = flow.price
            else:
                nbr = flow.quantity
            edge = FlowEdge(flow.from_function, flow.to_function, flow.resource_type.name, nbr)
            edges.append(edge)
        prev = flow                  
    for edge in edges:
        width = 1
        if total > 0:
            width = round((edge.quantity / total), 2) * 50
            width = int(width)
        edge.width = width
    template_params =  {
        'cluster': cluster,
        'nodes': nodes,
        'edges': edges,
    }
    return template_params

def agent_flow_params(cluster, toggle):
    template_params = {}
    flows = AgentResourceFlow.objects.filter(
        from_function__function__cluster=cluster)
    nodes = []
    if toggle == "price":
        total = Decimal("0.00")
    else:
        total = 0.0
    for flow in flows:
        nodes.extend([flow.from_function, flow.to_function])
        if toggle == "val":
            total += flow.get_value()
        elif toggle == "price":
            total += flow.price
        else:
            total += flow.quantity
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
            if toggle == "val":
                edge.quantity += flow.get_value()
            elif toggle == "price":
                edge.quantity += flow.price
            else:
                edge.quantity += flow.quantity
        else:
            if toggle == "val":
                nbr = flow.get_value()
            elif toggle == "price":
                nbr = flow.price
            else:
                nbr = flow.quantity
            edge = FlowEdge(flow.from_function, flow.to_function, flow.resource_type.name, nbr)
            edges.append(edge)
        prev = flow                  
    for edge in edges:
        width = 1
        if total > 0:
            width = round((edge.quantity / total), 2) * 50
            width = int(width)
        edge.width = width
    template_params =  {
        'cluster': cluster,
        'nodes': nodes,
        'edges': edges,
    }
    return template_params
         
def flow_params(cluster, toggle):
    template_params = {}
    flows = FunctionResourceFlow.objects.filter(
        from_function__cluster=cluster)
    nodes = []
    if toggle == "price":
        total = Decimal("0.00")
    else:
        total = 0.0
    for flow in flows:
        nodes.extend([flow.from_function, flow.to_function])
        if toggle == "val":
            total += flow.get_value()
        elif toggle == "price":
            total += flow.price
        else:
            total += flow.quantity
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
            if toggle == "val":
                edge.quantity += flow.get_value()
            elif toggle == "price":
                edge.quantity += flow.price
            else:
                edge.quantity += flow.quantity
        else:
            if toggle == "val":
                nbr = flow.get_value()
            elif toggle == "price":
                nbr = flow.price
            else:
                nbr = flow.quantity
            edge = FlowEdge(flow.from_function, flow.to_function, flow.resource_type.name, nbr)
            edges.append(edge)
        prev = flow                  
    for edge in edges:
        width = 1
        if total > 0:
            width = round((edge.quantity / total), 2) * 50
            width = int(width)
        edge.width = width
    template_params =  {
        'cluster': cluster,
        'nodes': nodes,
        'edges': edges,
    }
    return template_params
    
def flows(request, cluster_id, toggle="qty", level="fn"):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    toggle_form = QuantityPriceValueForm(
        initial={"toggle": toggle,},
        data=request.POST or None)
    level_form = None
    if cluster.agents():
        level_form = FunctionAgentLevelForm(
            initial={"level": level,},
            data=request.POST or None)
    if request.method == "POST":
        if level_form:
            if level_form.is_valid():
                level = level_form.cleaned_data["level"]
        if toggle_form.is_valid():
            toggle = toggle_form.cleaned_data["toggle"]
        return HttpResponseRedirect('/%s/%s/%s/%s/'
                    % ('clusters/flows', cluster_id, toggle, level))
    if level == "agt":
        template_params = agent_flow_params(cluster, toggle)
    elif level == "grp":
        template_params = group_flow_params(cluster, toggle)
    else:
        template_params = flow_params(cluster, toggle)
    template_params["use_window_size"] = True
    template_params["toggle_form"] = toggle_form
    template_params["level_form"] = level_form
    #if request.method == "POST":
    #    if toggle_form.is_valid():
            #import pdb; pdb.set_trace()
    #        tog = toggle_form.cleaned_data["toggle"]
    #        return HttpResponseRedirect('/%s/%s/%s/'
    #            % ('clusters/flows', cluster_id, tog))
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
    
    
def explore(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    template_params = explore_params(cluster)
    
    return render_to_response("clusters/explore.html", 
        template_params,
        context_instance=RequestContext(request))

    
def diagnostics(request, cluster_id, level="fn"):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    symbol = "$"
    try:
        symbol = cluster.community.unit_of_value.symbol
    except:
        pass
    
    level_form = None
    if cluster.agents():
        level_form = FunctionAgentTwoLevelForm(
            initial={"level": level,},
            data=request.POST or None)
        
    if request.method == "POST":
        if level_form:
            if level_form.is_valid():
                level = level_form.cleaned_data["level"]
        return HttpResponseRedirect('/%s/%s/%s/'
                    % ('clusters/diagnostics', cluster_id, level))
    
    function_io_vs_flows = []
    if level == "agt":
        function_production_without_consumption = cluster.agent_function_production_without_consumption()
        function_consumption_without_production = cluster.agent_function_consumption_without_production()
        #if cluster.has_flows():
            #function_io_vs_flows = cluster.agent_io_vs_flows()
    else:
        function_production_without_consumption = cluster.function_production_without_consumption()
        function_consumption_without_production = cluster.function_consumption_without_production()
        if cluster.has_flows():
            function_io_vs_flows = cluster.function_io_vs_flows()
    
    return render_to_response("clusters/diagnostics.html",{ 
        "cluster": cluster,
        "symbol": symbol,
        "level_form": level_form,
        "function_production_without_consumption": function_production_without_consumption,
        "function_consumption_without_production": function_consumption_without_production,
        "function_io_vs_flows": function_io_vs_flows,
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
def edit_function(request, function_id):
    fn = get_object_or_404(EconomicFunction, pk=function_id)
    cluster = fn.cluster
    function_form = EconomicFunctionForm(data=request.POST or None, instance=fn)
    function_aspect_name = cluster.function_aspect_name
    if request.method == "POST":
        if function_form.is_valid():
            function_form.save()
            return HttpResponseRedirect('/%s/%s/'
               % ('clusters/editclusterfunctions', cluster.id))
    return render_to_response("clusters/edit_function.html",{ 
        "function": fn,
        "cluster": cluster,
        "function_aspect_name": function_aspect_name,
        "function_form": function_form,
    }, context_instance=RequestContext(request))

@login_required    
def delete_function(request, function_id):
    fn = get_object_or_404(EconomicFunction, pk=function_id)
    
    return render_to_response("clusters/economic_functions.html",{ 
        "function": fn,
    }, context_instance=RequestContext(request))


@login_required    
def delete_function_confirmation(request, function_id):
    fn = get_object_or_404(EconomicFunction, pk=function_id)
    consequences = False
    function_resources = fn.resources.all()
    incoming_flows = fn.incoming_flows.all()
    outgoing_flows = fn.outgoing_flows.all()
    agent_functions = fn.agents.all()
    if function_resources or incoming_flows or outgoing_flows or agent_functions:
        consequences = True
    return render_to_response("clusters/economic_functions.html",{ 
        "function": fn,
        "consequences": consequences,
        "function_resources": function_resources,
        "incoming_flows": incoming_flows,
        "outgoing_flows": outgoing_flows,
        "agent_functions": agent_functions,
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
def new_agent_function(request, cluster_id):
    if request.method == "POST":
        next = request.POST.get("next")
        cluster = get_object_or_404(Cluster, pk=cluster_id)
        form = InlineAgentFunctionForm(data=request.POST, cluster=cluster, prefix="function")
        #import pdb; pdb.set_trace()
        if form.is_valid():
            data = form.cleaned_data
            agent = data["agent"]
            name = data["name"]
            aspect = data["aspect"]
            funs = EconomicFunction.objects.filter(
                cluster=cluster,
                name=name)
            if funs:
                fun = funs[0]
                if aspect:
                    if aspect != fun.aspect:
                        fun.aspect = aspect
                        fun.save()
            else:
                fun = EconomicFunction(
                    name=name,
                    cluster=cluster,
                    aspect=aspect)
                fun.save()
            af = AgentFunction(
                agent=agent,
                function=fun)
            af.save()        
    return HttpResponseRedirect(next)
    
@login_required 
def inline_new_agent_function(request, cluster_id, agent_id):
    if request.method == "POST":
        cluster = get_object_or_404(Cluster, pk=cluster_id)
        agent = get_object_or_404(EconomicAgent, pk=agent_id)
        form = AgentFunctionCreationForm(data=request.POST, prefix="function")
        #import pdb; pdb.set_trace()
        #print "b4 form validity check"
        if form.is_valid():
            #print "after form validity check"
            name = form.cleaned_data["name"]
            aspect = form.cleaned_data["aspect"]
            funs = EconomicFunction.objects.filter(
                cluster=cluster,
                name=name)
            if funs:
                fun = funs[0]
                if aspect:
                    if aspect != fun.aspect:
                        fun.aspect = aspect
                        fun.save()
            else:
                fun = EconomicFunction(
                    name=name,
                    cluster=cluster,
                    aspect=aspect)
                fun.save()
            af = AgentFunction(
                agent=agent,
                function=fun)
            af.save()
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
def new_community(request):
    form = CommunityForm(data=request.POST or None)
    map_key = settings.GOOGLE_API_KEY
    if request.method == "POST":
        #import pdb; pdb.set_trace()
        if form.is_valid():
            form.save()
            return redirect("clusters")
    return render_to_response("clusters/new_community.html",{ 
        "form": form,
        "map_key": map_key,
    }, context_instance=RequestContext(request))
    
@login_required    
def new_cluster(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    form = ClusterForm(data=request.POST or None)
    if request.method == "POST":
        #import pdb; pdb.set_trace()
        if form.is_valid():
            cluster = form.save(commit=False)
            cluster.community = community
            cluster.save()
            return redirect("clusters")
    return render_to_response("clusters/new_cluster.html",{ 
        "form": form,
        "community": community,
    }, context_instance=RequestContext(request))
    
@login_required    
def edit_cluster(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    community = cluster.community
    form = ClusterForm(instance=cluster, data=request.POST or None)
    if request.method == "POST":
        #import pdb; pdb.set_trace()
        if form.is_valid():
            cluster = form.save(commit=False)
            cluster.community = community
            cluster.save()
            return HttpResponseRedirect('/%s/%s/'
               % ('clusters/cluster', cluster_id))
    return render_to_response("clusters/edit_cluster.html",{ 
        "form": form,
        "cluster": cluster,
    }, context_instance=RequestContext(request))
    
@login_required    
def edit_community(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    form = CommunityForm(instance=community, data=request.POST or None)
    map_center = "0, 0"
    if community.latitude and community.longitude:
        map_center = ",".join([str(community.latitude), str(community.longitude)])
    map_key = settings.GOOGLE_API_KEY
    if request.method == "POST":
        #import pdb; pdb.set_trace()
        if form.is_valid():
            form.save()
            return redirect("clusters")
    return render_to_response("clusters/edit_community.html",{ 
        "form": form,
        "community": community,
        "map_center": map_center,
        "map_key": map_key,
    }, context_instance=RequestContext(request))    

@login_required    
def new_cluster_agent(request, cluster_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    community = cluster.community
    area_name = community.agent_geographic_area_name
    map_center = ",".join([str(community.latitude), str(community.longitude)])
    map_key = settings.GOOGLE_API_KEY
    zoom_level = community.map_zoom_level - 1
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
            ca, created = CommunityAgent.objects.get_or_create(community=cluster.community, agent=agent)
            ca.group = data["group"]
            if area_name:
                ca.geographic_area = data["geographic_area"]
                ca.region_latitude = data["region_latitude"]
                ca.region_longitude = data["region_longitude"]
            ca.save()
            return HttpResponseRedirect('/%s/%s/%s/'
               % ('clusters/editclusteragent', cluster_id, agent.id))
    return render_to_response("clusters/new_cluster_agent.html",{ 
        "cluster": cluster,
        "map_center": map_center,
        "map_key": map_key,
        "zoom_level": zoom_level,
        "form": form,
        "agent_names": agent_names,
        "area_name": area_name,
    }, context_instance=RequestContext(request))

@login_required    
def edit_cluster_agent(request, cluster_id, agent_id):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    agent = get_object_or_404(EconomicAgent, pk=agent_id)
    community = cluster.community
    agent_communities = agent.communities.all()
    edit_address = True
    if agent_communities.count() > 1:
        edit_address = False
    if agent_communities[0].community.id != community.id:
        edit_address = False
    #import pdb; pdb.set_trace()
    agent.cluster_funs = agent.functions.filter(
        function__cluster=cluster)
    for cf in agent.cluster_funs:
        cf.rsrcs = cf.function.resources.all()
        if cf.rsrcs:
            for res in cf.rsrcs:
                agent_function = agent.functions.get(function=res.function)
                init = {"agent_function_id": agent_function.id,}
                res.agent_resource_form = AgentFunctionResourceForm(res, initial=init)
                res.agent_resource_list = res.function_resources_for_agent(agent)                
        else:
            cf.agent_resources = cf.function_resources.all()
            init = {"agent_function_id": cf.id,}
            cf.agent_resource_form = AgentFunctionResourceForm(initial=init)
        outliers = []
        candidates = cf.function_resources.all()
        for c in candidates:
            if c.is_outlier():
                outliers.append(c)
        cf.outliers = outliers
    new_function_form = AgentFunctionCreationForm(prefix="function")
    resource_names = '~'.join([res.name for res in EconomicResourceType.objects.all()])
    used = [(af.function.id) for af in agent.functions.all()]
    function_names = '~'.join([fn.name for fn in cluster.functions.all().exclude(id__in=used)])
    template_params = agent_network_params(cluster, "qty")
    template_params["cluster"] = cluster
    template_params["agent"] = agent
    template_params["edit_address"] = edit_address
    template_params["cluster_funs"] = agent.cluster_funs
    template_params["new_function_form"] = new_function_form
    template_params["resource_names"] = resource_names
    template_params["function_names"] = function_names
    function_aspect_name = cluster.function_aspect_name
    resource_aspect_name = cluster.community.resource_aspect_name
    template_params["function_aspect_name"] = function_aspect_name
    template_params["resource_aspect_name"] = resource_aspect_name
    return render_to_response("clusters/edit_cluster_agent.html",
        template_params, 
        context_instance=RequestContext(request))
    
@login_required    
def edit_agent_address(request, cluster_id, agent_id):
    agent = get_object_or_404(EconomicAgent, pk=agent_id)
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    community = cluster.community
    ca = CommunityAgent.objects.get(community=community, agent=agent)
    area_name = community.agent_geographic_area_name
    map_center = "0, 0"
    if community.latitude and community.longitude:
        map_center = ",".join([str(community.latitude), str(community.longitude)])
    map_key = settings.GOOGLE_API_KEY
    zoom_level = 0
    if community.map_zoom_level:
        zoom_level = community.map_zoom_level - 1
    init = {
        "group": ca.group,
        "geographic_area": ca.geographic_area,
        "region_latitude": ca.region_latitude,
        "region_longitude": ca.region_longitude,
    }
    agent_form = EconomicAgentForm(instance=agent, initial=init, data=request.POST or None)
    if request.method == "POST":
        if agent_form.is_valid():
            data = agent_form.cleaned_data
            ca.group = data["group"]
            if area_name:
                ca.geographic_area = data["geographic_area"]
                ca.region_latitude = data["region_latitude"]
                ca.region_longitude = data["region_longitude"]
            ca.save()
            agent_form.save()
            return HttpResponseRedirect('/%s/%s/'
               % ('clusters/clusteragents', cluster_id))
    return render_to_response("clusters/edit_agent_address.html",{ 
        "cluster": cluster,
        "agent": agent,
        "agent_form": agent_form,
        "map_center": map_center,
        "map_key": map_key,
        "zoom_level": zoom_level,
        "area_name": area_name,
    }, context_instance=RequestContext(request))
    
    
@login_required    
def edit_community_agent(request, cluster_id, agent_id):
    agent = get_object_or_404(EconomicAgent, pk=agent_id)
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    community = cluster.community
    ca = CommunityAgent.objects.get(community=community, agent=agent)
    area_name = community.agent_geographic_area_name
    map_center = "0, 0"
    if community.latitude and community.longitude:
        map_center = ",".join([str(community.latitude), str(community.longitude)])
    map_key = settings.GOOGLE_API_KEY
    zoom_level = 0
    if community.map_zoom_level:
        zoom_level = community.map_zoom_level - 1
    agent_form = EditCommunityAgentForm(instance=ca, data=request.POST or None)
    if request.method == "POST":
        if agent_form.is_valid():
            agent_form.save()
            return HttpResponseRedirect('/%s/%s/'
               % ('clusters/clusteragents', cluster_id))
    return render_to_response("clusters/edit_community_agent.html",{ 
        "cluster": cluster,
        "community": community,
        "community_agent": ca,
        "agent": agent,
        "agent_form": agent_form,
        "map_center": map_center,
        "map_key": map_key,
        "zoom_level": zoom_level,
        "area_name": area_name,
    }, context_instance=RequestContext(request))
    
def json_agent_address(request, agent_name):
    # Note: serializer requires an iterable, not a single object. Thus filter rather than get.  
    data = serializers.serialize("json", EconomicAgent.objects.filter(name=agent_name), fields=('address',))    
    return HttpResponse(data, mimetype="text/json-comment-filtered")

def json_resource_unit(request, name):
    # Note: serializer requires an iterable, not a single object. Thus filter rather than get.
    data = serializers.serialize("json", EconomicResourceType.objects.filter(name=name), fields=('unit_of_quantity',))
    return HttpResponse(data, mimetype="text/json-comment-filtered")

def json_resource_aspect(request, name, community_id):
    #import pdb; pdb.set_trace()
    community = get_object_or_404(Community, id=community_id)
    erts = EconomicResourceType.objects.filter(name=name)
    ert = erts[0]
    qs = CommunityResourceType.objects.filter(community=community, resource_type=ert)
    data = serializers.serialize("json", qs, fields=('aspect',))
    return HttpResponse(data, mimetype="text/json-comment-filtered")

def json_function_aspect(request, function_name, cluster_id):
    #import pdb; pdb.set_trace()
    cluster = get_object_or_404(Cluster, id=cluster_id)
    qs = EconomicFunction.objects.filter(cluster=cluster, name=function_name)
    data = serializers.serialize("json", qs, fields=('aspect',))
    return HttpResponse(data, mimetype="text/json-comment-filtered")

def change_function_resource_amount(request):
    id = request.POST.get("id")
    quantity = request.POST.get("quantity")
    frt = get_object_or_404(FunctionResourceType, pk=id)
    #import pdb; pdb.set_trace()
    quantity = int(quantity)
    if quantity != frt.quantity:
        frt.quantity = quantity
        frt.save()
    data = "ok"
    return HttpResponse(data, mimetype="text/plain")

def change_function_resource_value(request):
    id = request.POST.get("id")
    value = request.POST.get("value")
    frt = get_object_or_404(FunctionResourceType, pk=id)
    #import pdb; pdb.set_trace()
    value = int(value)
    if value != frt.value:
        frt.value = value
        frt.save()
    data = "ok"
    return HttpResponse(data, mimetype="text/plain")

def change_function_resource_price(request):
    id = request.POST.get("id")
    price = request.POST.get("price")
    frt = get_object_or_404(FunctionResourceType, pk=id)
    #import pdb; pdb.set_trace()
    price = int(price)
    if price != frt.price:
        frt.price = price
        frt.save()
    data = "ok"
    return HttpResponse(data, mimetype="text/plain")

def change_agent_function_resource_amount(request):
    id = request.POST.get("id")
    quantity = request.POST.get("quantity")
    frt = get_object_or_404(AgentFunctionResourceType, pk=id)
    #import pdb; pdb.set_trace()
    quantity = int(quantity)
    if quantity != frt.quantity:
        frt.quantity = quantity
        frt.save()
    data = "ok"
    return HttpResponse(data, mimetype="text/plain")

def change_agent_function_resource_value(request):
    id = request.POST.get("id")
    value = request.POST.get("value")
    frt = get_object_or_404(AgentFunctionResourceType, pk=id)
    #import pdb; pdb.set_trace()
    value = int(value)
    if value != frt.value:
        frt.value = value
        frt.save()
    data = "ok"
    return HttpResponse(data, mimetype="text/plain")

def change_agent_function_resource_price(request):
    id = request.POST.get("id")
    price = request.POST.get("price")
    frt = get_object_or_404(AgentFunctionResourceType, pk=id)
    #import pdb; pdb.set_trace()
    price = int(price)
    if price != frt.price:
        frt.price = price
        frt.save()
    data = "ok"
    return HttpResponse(data, mimetype="text/plain")

def delete_function_resource(request, id):
    frt = get_object_or_404(FunctionResourceType, pk=id)
    cluster = frt.function.cluster
    frt.delete()
    return HttpResponseRedirect('/%s/%s/'
        % ('clusters/editclusterfunctions', cluster.id))
    
def delete_agent_function_resource(request, id):
    frt = get_object_or_404(AgentFunctionResourceType, pk=id)
    cluster = frt.agent_function.function.cluster
    agent = frt.agent_function.agent
    frt.delete()
    return HttpResponseRedirect('/%s/%s/%s/'
        % ('clusters/editclusteragent', cluster.id, agent.id))

@login_required    
def inline_new_resource(request, cluster_id):
    if request.method == "POST":
        next = request.POST.get("next")
        cluster = get_object_or_404(Cluster, pk=cluster_id)
        form = EconomicResourceTypeForm(request.POST, prefix="resource")
        if form.is_valid():
            data = form.cleaned_data
            name = data['name']
            aspect = data['aspect']
            try:
                resource = EconomicResourceType.objects.get(name=name)
            except EconomicResourceType.DoesNotExist:
                resource = form.save()
            crt, created = CommunityResourceType.objects.get_or_create(
                community=cluster.community, resource_type=resource)
            if aspect:
                if aspect != crt.aspect:
                    crt.aspect = aspect
                    crt.save()
    return HttpResponseRedirect(next)

@login_required    
def inline_agent_resource(request, cluster_id, agent_id, parent_id):
    if request.method == "POST":
        agent = get_object_or_404(EconomicAgent, pk=agent_id)
        parent_id = int(parent_id)
        if parent_id:
            parent = get_object_or_404(EconomicResourceType, pk=parent_id)
        else:
            parent = None
        cluster = get_object_or_404(Cluster, pk=cluster_id)
        form = AgentFunctionResourceForm(function_resource=None, data=request.POST)
        #import pdb; pdb.set_trace()
        if form.is_valid():
            data = form.cleaned_data
            name = data['name']
            role = data['role']
            quantity = data['quantity']
            price = data['price']
            agent_function_id = data['agent_function_id']
            new_resource = True
            
            #import pdb; pdb.set_trace()
            
            try:
                resource = EconomicResourceType.objects.get(name=name)
                new_resource = False
                if parent:
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
            agent_function = AgentFunction.objects.get(id=agent_function_id)
            AgentFunctionResourceType(
                resource_type=resource, 
                agent_function=agent_function, 
                role=role, 
                quantity=quantity,
                price=price).save()
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
        
    
def fr_table(request, cluster_id, toggle="qty"):
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    toggle_form = QuantityValueForm(
        initial={"toggle": toggle,},
        data=request.POST or None)
    frtable = function_resource_table(cluster, toggle)
    if request.method == "POST":
        if toggle_form.is_valid():
            tog = toggle_form.cleaned_data["toggle"]
            return HttpResponseRedirect('/%s/%s/%s/'
                % ('clusters/frtable', cluster_id, tog))
    
    return render_to_response("clusters/fr_table.html",{ 
        "cluster": cluster,
        "frtable": frtable,
        "toggle_form": toggle_form,
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

def object_filter(request, cluster_id=None, model=None, queryset=None, template_name=None, extra_context=None,
    context_processors=None, filter_class=None, page_length=None, page_variable="p"):
    #import pdb; pdb.set_trace()
    if cluster_id:
        cluster = get_object_or_404(Cluster, pk=cluster_id)
        queryset = filter_class.queryset(cluster)
    if model is None and filter_class is None:
        raise TypeError("object_filter must be called with either model or filter_class")
    if model is None:
        model = filter_class._meta.model
    if filter_class is None:
        meta = type('Meta', (object,), {'model': model})
        filter_class = type('%sFilterSet' % model._meta.object_name, (FilterSet,),
            {'Meta': meta})
    
    #import pdb; pdb.set_trace()    
    filterset = filter_class(request.GET or None, queryset=queryset)
    
    if not template_name:
        template_name = '%s/%s_filter.html' % (model._meta.app_label, model._meta.object_name.lower())
    c = RequestContext(request, {
        'filter': filterset,
        })
    if extra_context:
        for k, v in extra_context.iteritems():
            if callable(v):
                v = v()
            c[k] = v
    
    if page_length:
        from django.core.paginator import Paginator
        p = Paginator(filterset.qs,page_length)
        getvars = request.GET.copy()
        if page_variable in getvars:
            del getvars[page_variable]
        if len(getvars.keys()) > 0:
            p.querystring = "&%s" % getvars.urlencode()
        try:
            c['paginated_filter'] = p.page(request.GET.get(page_variable,1))
        except EmptyPage:
            raise Http404
        
        c['paginator'] = p
    
    return render_to_response(template_name, c)
