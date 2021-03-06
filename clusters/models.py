import re
from decimal import *

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from clusters.utils import *
from clusters.tarjan import strongly_connected_components

class InputOutputCell(object):
    def __init__(self, producer, consumer, resource):
         self.producer = producer
         self.consumer = consumer
         self.resource = resource
    
class InputOutputTable(object):
    def __init__(self, columns, rows):
         self.columns = columns
         self.rows = rows
         
class InputOutputHeader(object):
    def __init__(self, function, resources):
         self.function = function
         self.resources = resources     

def input_output_cells(cluster):
    cells = []
    for ef in EconomicFunction.objects.filter(cluster=cluster):
        outputs = ef.outputs()
        if outputs:
            for output in ef.outputs():
                for fn_rt in output.resource_type.functions.filter(role="consumes"):
                    cells.append(InputOutputCell(ef, fn_rt.function, output.resource_type))
    return cells

# todo: what if one EconomicFunction provides more than one input
# to the same consuming EconomicFunction?

def input_output_table(cluster):
    # todo: rows and columns shd be sorted the same
    cells = input_output_cells(cluster)
    rows = {}
    columns = []
    for cell in cells:
        columns.append(cell.consumer)
    columns = list(set(columns))
    col_count = len(columns)
    for cell in cells:
        rows[cell.producer] = []
        for x in range(col_count):
            rows[cell.producer].append(' ')
    for cell in cells:
        row_cell = columns.index(cell.consumer)
        rows[cell.producer][row_cell] = cell.resource
    return InputOutputTable(columns, rows)

class FunctionResourceTable(object):
    def __init__(self, columns, rows):
         self.columns = columns
         self.rows = rows

def function_resource_table(cluster, toggle):
    frs = FunctionResourceType.objects.filter(function__cluster=cluster)
    functions = {}
    resources = []
    for fr in frs:
        resources.append(fr.resource_type)
    resources = list(set(resources))
    resources.sort(lambda x, y: cmp(x.name, y.name))
    col_count = len(resources)
    for fr in frs:
        function = fr.function
        if not function in functions:
            functions[function] = [function.name,]
            for x in range(col_count + 1):
                functions[function].append('')
            functions[function][col_count + 1] = 0
    for fr in frs: 
        mult = 1
        if fr.role == "consumes":
            mult = -1
        row_cell = resources.index(fr.resource_type) + 1
        if toggle == "val":
            functions[fr.function][row_cell] = fr.value * mult
            functions[fr.function][col_count + 1] += fr.value * mult
        else:
            functions[fr.function][row_cell] = fr.quantity * mult
            functions[fr.function][col_count + 1] += fr.quantity * mult
    rows = functions.values()
    rows.sort()
    col_totals = ["Totals",]
    for i in range(1, col_count + 2):
        col_totals.append(0)
    for row in rows:
        for i in range(1, col_count + 2):
            col_totals[i] += row[i] or 0
    rows.append(col_totals)
    columns = []
    for r in resources:
        columns.append(r.name)
    columns.append("Totals")
    return FunctionResourceTable(columns, rows)

def connected_functions(node, all_nodes, to_return):
    to_return.append(node)
    for subnode in all_nodes:
        for out in subnode.outputs():
            for consumer in out.resource_type.cluster_consumers(subnode.cluster):
                if not consumer.function in to_return:
                    connected_functions(consumer.function, all_nodes, to_return)
        for inp in subnode.inputs():
            for producer in inp.resource_type.cluster_producers(subnode.cluster):
                if not producer.function in to_return:
                    connected_functions(producer.function, all_nodes, to_return)
    return to_return
 
UNIT_TYPE_CHOICES = (
    ('quantity', 'quantity'),
    ('value', 'value'),
)
 
 
class Unit(models.Model):
     type = models.CharField(max_length=12, choices=UNIT_TYPE_CHOICES)
     abbrev = models.CharField(max_length=8)
     name = models.CharField(max_length=64)
     symbol = models.CharField(max_length=1, blank=True)
     
     def __unicode__(self):
        return self.abbrev
     

class Community(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    map_center = models.CharField(max_length=255, blank=True,
        help_text="Map center may be an address, or latitude and longitude.")
    latitude = models.FloatField(default=0.0, blank=True, null=True)
    longitude = models.FloatField(default=0.0, blank=True, null=True)
    map_zoom_level = models.PositiveSmallIntegerField(default=0,
        help_text="0-20 - larger numbers zoom in more")
    unit_of_value = models.ForeignKey(Unit, blank=True, null=True,
        limit_choices_to={"type": "value"},
        related_name="community_units")
    resource_aspect_name = models.CharField(max_length=128, blank=True,
        help_text="Name for aspect fields on Economic Resource Types in this community.  If no name, aspects will not be used.")
    agent_geographic_area_name = models.CharField(max_length=128, blank=True,
        help_text="Name for geographic area fields for Economic Agents in this community.  If no name, areas will not be used.")
    when_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(User, verbose_name='created by',
        related_name='created_community', blank=True, null=True)
    when_changed = models.DateTimeField(auto_now=True, blank=True, null=True)
    changed_by = models.ForeignKey(User, verbose_name='changed by',
        related_name='changed_community', blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "communities"
        ordering = ('name',)
        
    def __unicode__(self):
        return self.name
    
    def is_public(self):
        answer = False
        for cluster in self.clusters.all():
            if cluster.is_public():
                answer = True
                break
        return answer
    
    def member_users(self):
        return [m.member for m in self.members.all()]
    
    def permits(self, perm_name, user):
        if user.is_superuser:
            return True
        if self.created_by:
            if user.id == self.created_by.id:
                return True
        perm = None
        mbr = [mbr for mbr in self.members.all() if mbr.member.id == user.id]
        if mbr:
            mbr = mbr[0]
            perm = mbr.permission_role
        if perm_name == "delete" or perm_name == "users":
            if perm:
                if perm == "owner":
                    return True
            else:
                return False
        else:
            if perm:
                return True
        return False



PERMISSION_ROLE_CHOICES = (
    ('owner', 'Owner'),
    ('editor', 'Editor'),
)


class CommunityMember(models.Model):
    community = models.ForeignKey(Community, related_name='members')
    member = models.ForeignKey(User, related_name="communities")
    permission_role = models.CharField(max_length=12, choices=PERMISSION_ROLE_CHOICES)
    
    @property
    def username(self):
        return self.member.username

class AggregateFunctionResource(object):
    def __init__(self, function, resource_type, role, quantity, price, value):
        self.function = function
        self.resource_type = resource_type
        self.role = role
        self.quantity = quantity
        self.price = price
        self.value = value
        
    def get_value(self):
        if self.value:
            return self.value
        if self.quantity and self.price:
            return int((self.quantity * self.price).quantize(Decimal('.01'), rounding=ROUND_UP))
        return 0
        
    @property
    def color(self):
        return "green"

   
class AgentGroupFlow(object):
    def __init__(self, from_function, to_function, resource_type, quantity, price, value):
        self.from_function = from_function
        self.to_function = to_function
        self.resource_type = resource_type
        self.quantity = quantity
        self.price = price
        self.value = value
        
    def get_value(self):
        if self.value:
            return self.value
        if self.quantity and self.price:
            return int((self.quantity * self.price).quantize(Decimal('.01'), rounding=ROUND_UP))
        return 0
        
    @property
    def color(self):
        return "green"

   
class AgentGroupFunction(object):
    def __init__(self, function, flow_dict):
        self.function = function
        self.flow_dict = flow_dict
        
    def flows(self):
        return self.flow_dict.values()
        
    @property
    def color(self):
        return "green"
 

class AggregateFunction(object):
    def __init__(self, function, resource_dict):
        self.function = function
        self.resource_dict = resource_dict
        
    def resources(self):
        return self.resource_dict.values()
    
    def produced_function_resources(self):
        answer = []
        for r in self.resources():
            if r.role == "produces":
                answer.append(r)
        return answer
    
    def function_inputs(self):
        return [res for res in self.resources() if res.role == "consumes"]
    
    def function_outputs(self):
        return [res for res in self.resources() if res.role == "produces"]
        

class Region(object):
    def __init__(self, name, lat, lng, function_dict):
        self.name = name
        self.lat = lat
        self.lng = lng
        self.function_dict= function_dict
        
    def all_functions(self):
        return self.function_dict.values()
        
    def lat_lng(self):
        return ",".join([str(self.lat), str(self.lng)])
    
    def color(self):
        answer = "gray"
        not_green = ""
        for agfn in self.all_functions():
            if agfn.function.color != "green":
                not_green = agfn.function.color
        if not_green:
            answer = not_green
        else:
            answer = "green"
        return answer
            
    
class AgentGroup(object):
    def __init__(self, name, function_dict):
        self.name = name
        self.function_dict= function_dict
        
    def node_id(self):
        return "".join(["AgentGroup-", self.name])
        
    def all_functions(self):
        return self.function_dict.values()
    
    def function_inputs(self):
        fns = self.all_functions()
        answer = []
        for fn in fns:
            answer.extend(fn.function_inputs())
        return answer
    
    def function_outputs(self):
        fns = self.all_functions()
        answer = []
        for fn in fns:
            answer.extend(fn.function_outputs())
        return answer
        
    @property
    def color(self):
        return "firebrick"
        
        

class ResourceAtStage(object):
    def __init__(self, long_name):
        self.long_name = long_name
        self.name = long_name.split(";")[1]
        
    def node_id(self):
        return self.long_name

SHARING_CHOICES = (
    ('public', 'Public'),
    ('private', 'Private'),
)


class Cluster(models.Model):
    community = models.ForeignKey(Community, related_name='clusters')
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    function_aspect_name = models.CharField(max_length=128, blank=True,
        help_text="Name for aspect fields on Economic Functions in this cluster.  If no name, aspects will not be used.")
    root_function = models.ForeignKey("EconomicFunction", blank=True, null=True,
        related_name="cluster_root", 
        help_text="Graph root is optional - can be either function or resource but not both")
    root_resource = models.ForeignKey("EconomicResourceType", blank=True, null=True,
        related_name="cluster_root", 
        help_text="Graph root is optional - can be either function or resource but not both")
    when_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(User, verbose_name='created by',
        related_name='created_cluster', blank=True, null=True)
    when_changed = models.DateTimeField(auto_now=True, blank=True, null=True)
    changed_by = models.ForeignKey(User, verbose_name='changed by',
        related_name='changed_cluster', blank=True, null=True)
    sharing = models.CharField(max_length=12, choices=SHARING_CHOICES,
        default="private")
    
    def get_absolute_url(self):
        return ('cluster', (), {"cluster_id": self.id})
    
    def __unicode__(self):
        return " ".join([self.community.name, self.name])
           
    def permits(self, perm_name, user):
        if user.is_superuser:
            return True
        if self.created_by:
            if user.id == self.created_by.id:
                return True
        perm = None
        mbr = [mbr for mbr in self.community.members.all() if mbr.member.id == user.id]
        if mbr:
            mbr = mbr[0]
            perm = mbr.permission_role
        if perm_name == "delete":
            if perm:
                if perm == "owner":
                    return True
            else:
                return False
        else:
            if perm:
                return True
        return False
    
    def is_public(self):
        return self.sharing == "public"

    def root(self):
        if self.root_function:
            return self.root_function
        elif self.root_resource:
            return self.root_resource
        else:
            return None
        
    def resources(self):
        answer = []
        for fun in self.functions.all():
            for r in fun.resources.all():
                answer.append(r.resource_type)
        flows = FunctionResourceFlow.objects.filter(
            from_function__cluster=self)
        for flow in flows:
            answer.append(flow.resource_type)
        for agent in self.agents():
            for af in agent.functions.filter(function__cluster=self):
                for afrt in af.function_resources.all():
                    answer.append(afrt.resource_type)
        return list(set(answer))
    
    def community_resources(self):
        community = self.community
        resources = self.resources()
        crs = []
        for r in resources:
            crs.append(r.communities.get(community=community))
        return crs
      
    def agents(self):
        answer = []
        #for fun in self.functions.all():
        #    for a in fun.agents.all():
        #        answer.append(a.agent)
        #answer = list(set(answer))
        answer = [cla.agent for cla in self.cluster_agents.all()]
        answer.sort(lambda x, y: cmp(x.name, y.name))
        return answer
    
    def flow_connected_functions(self):
        connected = []
        flows = self.flows()
        for flow in flows:
            connected.append(flow.from_function)
            connected.append(flow.to_function)
        connected = list(set(connected))
        return connected
    
    def disjoints(self):
        funs = self.functions.all().order_by("id")
        root = self.root_function
        if not root:
            if funs.count():
                root = funs[0]
        connected = connected_functions(root, funs, [])
        connected.extend(self.flow_connected_functions())
        connected = list(set(connected))
        disjoint = []
        for fun in funs:
            if not fun in connected:
                disjoint.append(fun)
        return disjoint
    
    def missing_function_numbers(self):
        funs = self.functions.all()
        missing = []
        for fun in funs:
            for res in fun.resources.all():
                if not res.quantity:
                    missing.append(res)
        return missing
    
    def missing_agent_numbers(self):
        agents = self.agents()
        missing = []
        for agent in agents:
            for res in agent.resources.all():
                if not res.quantity:
                    missing.append(res)
        return missing
    
    def function_production_without_consumption(self):
        #import pdb; pdb.set_trace()
        funs = self.functions.all()
        missing = []
        for fun in funs:
            for out in fun.outputs():
                consumption_qty = 0
                consumption_val = 0
                for consumer in out.resource_type.cluster_consumers(self):
                    consumption_qty += consumer.quantity
                    consumption_val += consumer.value
                if consumption_qty < out.quantity:
                    missing.append({"function_resource": out, "quantity_missing": consumption_qty - out.quantity })
                if consumption_val < out.value:
                    missing.append({"function_resource": out, "value_missing": consumption_val - out.value })
        return missing

    def function_consumption_without_production(self):
        #import pdb; pdb.set_trace()
        funs = self.functions.all()
        missing = []
        for fun in funs:
            for inp in fun.inputs():
                production_qty = 0
                production_val = 0
                for producer in inp.resource_type.cluster_producers(self):
                    production_qty += producer.quantity
                    production_val += producer.value
                if production_qty < inp.quantity:
                    missing.append({"function_resource": inp, "quantity_missing": production_qty - inp.quantity })
                if production_val < inp.value:
                    missing.append({"function_resource": inp, "value_missing": production_val - inp.value })
        return missing
    
    def agent_functions(self):
        return AgentFunction.objects.filter(function__cluster=self)
    
    def agent_function_production_without_consumption(self):
        #import pdb; pdb.set_trace()
        funs = self.agent_functions()
        missing = []
        for fun in funs:
            for out in fun.outputs():
                consumption_qty = 0
                consumption_val = 0
                for consumer in out.resource_type.cluster_consumers(self):
                    consumption_qty += consumer.quantity
                    consumption_val += consumer.value
                if consumption_qty < out.quantity:
                    missing.append({"function_resource": out, "quantity_missing": consumption_qty - out.quantity })
                if consumption_val < out.value:
                    missing.append({"function_resource": out, "value_missing": consumption_val - out.value })
        return missing

    def agent_function_consumption_without_production(self):
        #import pdb; pdb.set_trace()
        funs = self.agent_functions()
        missing = []
        for fun in funs:
            for inp in fun.inputs():
                production_qty = 0
                production_val = 0
                for producer in inp.resource_type.cluster_producers(self):
                    production_qty += producer.quantity
                    production_val += producer.value
                if production_qty < inp.quantity:
                    missing.append({"function_resource": inp, "quantity_missing": production_qty - inp.quantity })
                if production_val < inp.value:
                    missing.append({"function_resource": inp, "value_missing": production_val - inp.value })
        return missing
    
    def function_io_vs_flows(self):
        report = []
        fns = self.functions.all()
        #import pdb; pdb.set_trace()
        for fn in fns:
            incoming = fn.incoming_flows.all()
            for inc in incoming:
                inc.flow = True
                inc.matched = False
            outgoing = fn.outgoing_flows.all()
            for og in outgoing:
                og.flow = True
                og.matched = False
            for inp in fn.inputs():
                inp.flow = False
                report.append(inp)
                rels = inp.resource_type.all_relatives()
                for inc in incoming:
                    if inc.resource_type in rels:
                        inc.matched = True
                        report.append(inc)
            for outp in fn.outputs():
                outp.flow = False
                report.append(outp)
                rels = outp.resource_type.all_relatives()
                for og in outgoing:
                    if og.resource_type in rels:
                        og.matched = True
                        report.append(og)
            for inc in incoming:
                if not inc.matched:
                    report.append(inc)
            for og in outgoing:
                if not og.matched:
                    report.append(og)
        return report
                        
    def function_agent_diffs(self):
        #import pdb; pdb.set_trace()
        funs = self.functions.all()
        diffs = []
        for fun in funs:
            # agents here are AgentFunction objects
            agents = fun.agents.all()
            for res in fun.resources.all():
                agent_total_qty = 0
                agent_total_val = 0
                for agent in agents:
                    agent_total_qty += sum(
                        ares.quantity for ares in agent.function_resources.filter(
                            resource_type=res.resource_type, role=res.role)
                        )
                    agent_total_val += sum(
                        ares.value for ares in agent.function_resources.filter(
                            resource_type=res.resource_type, role=res.role)
                        )
                    for ares in agent.function_resources.filter(role=res.role):
                        if ares.resource_type.is_child_of(res.resource_type):
                            agent_total_qty += ares.quantity
                if agent_total_qty != res.quantity:
                    diffs.append({"function_resource": res, "function_quantity": res.quantity, "agent_total_qty": agent_total_qty})
                if agent_total_val != res.value:
                    diffs.append({"function_resource": res, "function_value": res.value, "agent_total_val": agent_total_val})
        return diffs
    
    def has_flows(self):
        flows = FunctionResourceFlow.objects.filter(
            from_function__cluster=self)
        if not flows:
            flows = AgentResourceFlow.objects.filter(
                from_function__function__cluster=self)
        if flows:
            return True
        else:
            return False
        
    def function_flows(self):
        return FunctionResourceFlow.objects.filter(
            from_function__cluster=self)
        
    def agent_flows(self):
        return AgentResourceFlow.objects.filter(
            from_function__function__cluster=self)
        
    def has_function_resources(self):
        frts = FunctionResourceType.objects.filter(
            function__cluster=self)
        if not frts:
            frts = AgentFunctionResourceType.objects.filter(
                agent_function__function__cluster=self)
        if frts:
            return True
        else:
            return False
        
    def fr_graph_nodes(self):
        fns = list(self.functions.all())
        rtypes = []
        for fn in fns:
            rtypes.extend([v.resource_type for v in fn.inputs()])
            rtypes.extend([v.resource_type for v in fn.outputs()])
        rtypes = list(set(rtypes))
        fns.extend(rtypes)
        return fns
        
    def flow_graph_nodes(self):
        flows = self.function_flows()
        nodes = []
        for flow in flows:
            nodes.append(flow.from_function)
            nodes.append(flow.to_function)
            nodes.append(flow.resource_type)
        nodes = list(set(nodes))
        return nodes
        
    def regions(self):
        areas = {}
        agents = self.agents()
        for agent in agents:
            co = self.community
            ca = CommunityAgent.objects.get(
                community=co, agent=agent)
            key = ca.region_latitude + ca.region_longitude
            if key:
                if not key in areas:
                    areas[key] = Region(
                        ca.geographic_area,
                        ca.region_latitude,
                        ca.region_longitude,
                        {})
                area = areas[key]
                afs = agent.functions.filter(function__cluster=self)
                for af in afs:
                    if not af.function.id in area.function_dict:
                        area.function_dict[af.function.id] = AggregateFunction(
                            af.function, {})
                    fn = area.function_dict[af.function.id]
                    for afrt in af.function_resources.all():
                        reskey = "".join([str(afrt.resource_type.id), afrt.role])
                        if not reskey in fn.resource_dict:
                            fn.resource_dict[reskey] = AggregateFunctionResource(
                                af.function, afrt.resource_type, afrt.role, 0.0, Decimal("0.00"), 0.0)
                        rt = fn.resource_dict[reskey]
                        rt.quantity += afrt.quantity
                        rt.price += afrt.price
                        rt.value += afrt.value
        return areas.values()
    
    def groups(self):
        groups = {}
        agents = self.agents()
        for agent in agents:
            co = self.community
            ca = CommunityAgent.objects.get(
                community=co, agent=agent)
            key = ca.group
            if key:
                if not key in groups:
                    groups[key] = AgentGroup(
                        ca.group,
                        {})
                grp = groups[key]
                afs = agent.functions.filter(function__cluster=self)
                #import pdb; pdb.set_trace()
                for af in afs:
                    if not af.function.id in grp.function_dict:
                        grp.function_dict[af.function.id] = AggregateFunction(
                            af.function, {})
                    fn = grp.function_dict[af.function.id]
                    for afrt in af.function_resources.all():
                        reskey = "".join([str(afrt.resource_type.id), afrt.role])
                        if not reskey in fn.resource_dict:
                            fn.resource_dict[reskey] = AggregateFunctionResource(
                                af.function, afrt.resource_type, afrt.role, 0, Decimal("0.00"), 0)
                        rt = fn.resource_dict[reskey]
                        rt.quantity += afrt.quantity
                        rt.price += afrt.price
                        rt.value += afrt.value
        return groups.values()
    
    def group_flows(self):
        groups = {}
        agents = self.agents()
        for agent in agents:
            co = self.community
            ca = CommunityAgent.objects.get(
                community=co, agent=agent)
            key = ca.group
            if key:
                if not key in groups:
                    groups[key] = AgentGroup(
                        ca.group,
                        {})
                grp = groups[key]
                afs = agent.functions.filter(function__cluster=self)
                for af in afs:
                    if not af.function.id in grp.function_dict:
                        grp.function_dict[af.function.id] = AgentGroupFunction(
                            af.function, {})
                    fn = grp.function_dict[af.function.id]
                    for flow in af.outgoing_flows.all():
                        flowkey = "-".join([
                            str(flow.from_function.function.id),
                            str(flow.to_function.function.id),
                            str(flow.resource_type.id),
                            ])
                        if not flowkey in fn.flow_dict:
                            fn.flow_dict[flowkey] = AgentGroupFlow(
                                flow.from_function.function,
                                flow.to_function.function,
                                flow.resource_type,
                                0.0, Decimal("0.00"), 0.0)
                        rt = fn.flow_dict[flowkey]
                        rt.quantity += flow.quantity
                        rt.price += flow.price
                        rt.value += flow.value
        group_flows = []
        for grp in groups.values():
            for fn in grp.all_functions():
                group_flows.extend(fn.flows())
        return group_flows
    
    def flow_bfs(self, start, resource_filter=None):
        visited=set([start])
        edges = []
        order = [start]
        # next(iter) lines commented out until locecon upgraded to python2.7
        #stack=[(start, iter(start.outflow_functions(resource_filter)))]
        stack=[(start, start.outflow_functions(resource_filter))]
        while stack:
            parent, children = stack[0]
            try:
                #child = next(children)
                child = children.pop(0)
                if child not in visited:
                    edges.append((parent, child))
                    visited.add(child)
                    order.append(child)
                    #stack.append((child, iter(child.outflow_functions(resource_filter))))
                    stack.append((child, child.outflow_functions(resource_filter)))
            #except StopIteration:
            except IndexError:
                stack.pop(0)
        return [edges, order]
    
    def flows(self):
        return FunctionResourceFlow.objects.filter(
                from_function__cluster=self)
        
    def toposort_flows(self):
        flows = self.flows()
        functions = [flow.from_function for flow in flows]
        functions.extend([flow.to_function for flow in flows])
        G = list(set(functions))
        for u in G:
            u.preds = [flow.from_function for flow in u.incoming_flows.all()]
            u.next = [flow.to_function for flow in u.outgoing_flows.all()]
        Q = [u for u in G if not u.preds]
        return toposort(G, Q)
    
    def toposort_frs(self):
        G = graphify(self)
        for u in G:
            u.preds = u.from_nodes(cluster)
            u.next = u.to_nodes(cluster)
        Q = [u for u in G if not u.preds]
        return toposort(G, Q)

    def cycles(self):
        frts = FunctionResourceType.objects.filter(
            function__cluster=self)
        graph = {}
        if frts:
            gc = self.fr_graph_nodes()
            for node in gc:
                graph[node] = node.to_nodes(self)
        else:
            flows = self.function_flows()
            for flow in flows:
                if not flow.from_function in graph:
                    graph[flow.from_function] = []
                rtype = ResourceAtStage(";".join([flow.from_function.name,flow.resource_type.name]))
                graph[flow.from_function].append(rtype)
                if not rtype in graph:
                    graph[rtype] = []
                graph[rtype].append(flow.to_function)

        #import pdb; pdb.set_trace()
        scc = strongly_connected_components(graph)
        cycles = []
        for sc in scc:
            if len(sc) > 1:
                cycles.append(sc)
        return cycles
    
    def has_cycles(self):
        if self.cycles():
            return True
        else:
            return False
    
    def value_added_rows(self, start, resource_filter=None):
        edges, order = self.flow_bfs(start, resource_filter)
        rows = []
        symbol = "$"
        try:
            symbol = cluster.community.unit_of_value.symbol
        except:
            pass
        for fn in order:
            rows.append(("Function:", fn.name, ""))
            costs, income, margin, margin_percent = fn.value_summary()
            rows.append(("", "Costs:", "".join([symbol, split_thousands(costs)])))
            rows.append(("", "Income:", "".join([symbol, split_thousands(income)])))
            rows.append(("", "Margin:", "".join([symbol, split_thousands(margin)])))
            rows.append(("", "Margin percent:", "".join([str(margin_percent), "%"])))
        return rows
    
    def function_colors(self):
        fns = self.functions.all()
        colors = {}
        #import pdb; pdb.set_trace()
        for fn in fns:
            if fn.agents.all():
                if not fn.color in colors:
                    colors[fn.color] = ""
                if colors[fn.color]:
                    colors[fn.color] = ", ".join([colors[fn.color], fn.name])
                else:
                    colors[fn.color] = fn.name
        return colors


class EconomicFunction(models.Model):
    cluster = models.ForeignKey(Cluster, related_name="functions")
    name = models.CharField(max_length=128)
    aspect = models.CharField(max_length=128, blank=True)
    color = models.CharField(max_length=12, choices=settings.COLOR_CHOICES,
        default="green")
    slug = models.SlugField("Page name", editable=False)
    
    class Meta:
        ordering = ('cluster', 'name',)
    
    def __unicode__(self):
        return " ".join([self.cluster.name, self.name])
    
    def save(self, *args, **kwargs):
        unique_slugify(self, self.name)
        super(EconomicFunction, self).save(*args, **kwargs)
        
    def value_summary(self):
        costs = sum(input.get_value() for input in self.incoming_flows.all())
        income = sum(input.get_value() for input in self.outgoing_flows.all())
        margin = income - costs
        if income:
            margin_percent = round(((float(margin) / income) * 100), 2)
        else:
            margin_percent = 0
        #print "margin:", margin, "income:", income, "margin_percent:", margin_percent
        return costs, income, margin, margin_percent
        
    def node_id(self):
        return "".join([ type(self).__name__, "-", self.slug])
    
    def inputs(self):
        return self.resources.filter(role="consumes")
    
    def outputs(self):
        return self.resources.filter(role="produces")
    
    def out_edges(self, cluster):
        return self.outputs()
    
    def out_edge_with(self, resource_type):
        try:
            return self.resources.get(
                role="produces", 
                resource_type=resource_type)
        except FunctionResourceType.DoesNotExist:
            return None
        
    def outflow_functions(self, resource_filter=None):
        if resource_filter:
            flows = self.outgoing_flows.filter(
                resource_type__name__icontains=resource_filter)
        else:
            flows = self.outgoing_flows.all()
        fns = []
        for flow in flows:
            if flow.to_function not in fns:
                fns.append(flow.to_function)
        return fns
    
    def from_nodes(self, cluster):
        # cluster is here only for duck typing
        # with EconomicResourceTypes
        return [v.resource_type for v in self.inputs()]
    
    def to_nodes(self, cluster):
        return [v.resource_type for v in self.outputs()]
    
    def flows(self):
        flows = list(self.incoming_flows.all())
        flows.extend(list(self.outgoing_flows.all()))
        return flows

# based on dfs from threaded_comments
def nested_objects(node, all_nodes):
     to_return = [node,]
     for subnode in all_nodes:
         if subnode.parent and subnode.parent.id == node.id:
             to_return.extend([nested_objects(subnode, all_nodes),])
     return to_return
 
def flattened_children(node, all_nodes, to_return):
     to_return.append(node)
     for subnode in all_nodes:
         if subnode.parent and subnode.parent.id == node.id:
             flattened_children(subnode, all_nodes, to_return)
     return to_return


class EconomicResourceType(models.Model):
    name = models.CharField(max_length=128)    
    parent = models.ForeignKey('self', blank=True, null=True, 
        related_name='children')
    slug = models.SlugField("Page name", editable=False)
    unit_of_quantity = models.ForeignKey(Unit, blank=True, null=True,
        limit_choices_to={"type": "quantity"},
        related_name="resource_units")
    
    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        unique_slugify(self, self.name)
        super(EconomicResourceType, self).save(*args, **kwargs)
        
    def node_id(self):
        return "".join([ type(self).__name__, "-", self.slug])
    
    def consumers(self):
        return self.functions.filter(role="consumes")
    
    def producers(self):
        return self.functions.filter(role="produces")
    
    def cluster_consumers(self, cluster):
        return self.functions.filter(role="consumes", function__cluster=cluster)
    
    def out_edges(self, cluster):
        return self.cluster_consumers(cluster)
    
    def out_edge_with(self, function):
        try:
            return self.functions.get(role="consumes", function=function)
        except FunctionResourceType.DoesNotExist:
            return None
               
    def cluster_producers(self, cluster):
        return self.functions.filter(role="produces", function__cluster=cluster)
    
    def from_nodes(self, cluster):
        return [v.function for v in self.cluster_producers(cluster)]
    
    def to_nodes(self, cluster):
        return [v.function for v in self.cluster_consumers(cluster)]
    
    def is_child_of(self, resource_type):
        if not self.parent:
            return False
        if self.parent.id == resource_type.id:
            return True
        res = self.parent
        while not res.parent is None:
            if res.parent.id == resource_type.id:
                return True
            res = res.parent
        return False
    
    def all_relatives(self):
        if self.parent:
            root = self.parent
            while not root.parent is None:
                root = root.parent
        else:
            root = self
        return flattened_children(root, EconomicResourceType.objects.all(), [])
        

    
class CommunityResourceType(models.Model):
    community = models.ForeignKey(Community, related_name='resources')
    resource_type = models.ForeignKey(EconomicResourceType, related_name='communities')
    aspect = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ('community', 'resource_type')
    
    def __unicode__(self):
        return " ".join([self.community.name, self.resource_type.name])


ROLE_CHOICES = (
    ('consumes', 'consumes'),
    ('produces', 'produces'),
)
    
class FunctionResourceType(models.Model):
    function = models.ForeignKey(EconomicFunction, related_name='resources')
    resource_type = models.ForeignKey(EconomicResourceType, related_name='functions')
    role = models.CharField(max_length=12, choices=ROLE_CHOICES)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal(0),
        help_text='If you enter Price and Quantity but not Value, Value will be computed as needed.')
    value = models.IntegerField(default=0)
    
    class Meta:
        ordering = ('function', 'role', 'resource_type',)
    
    def __unicode__(self):
        return " ".join([self.function.name, self.role, self.resource_type.name])
    
    def save(self, *args, **kwargs):
        if not self.pk:
            community = self.function.cluster.community
            rt = self.resource_type
            try:
                crt = CommunityResourceType.objects.get(community=community, resource_type=rt)
            except CommunityResourceType.DoesNotExist:
                crt = CommunityResourceType(community=community, resource_type=rt).save()
        super(FunctionResourceType, self).save(*args, **kwargs)
        
    def get_value(self):
        if self.value:
            return self.value
        if self.quantity and self.price:
            return int((self.quantity * self.price).quantize(Decimal('.01'), rounding=ROUND_UP))
        return 0
        
    def agent_resources(self):
        answer = []
        function_agents = self.function.agents.all()
        for fa in function_agents:
            for ar in fa.agent.resources.all():
                if ar.resource_type.id == self.resource_type.id and ar.role == self.role:
                    answer.append(ar)
                elif ar.resource_type.is_child_of(self.resource_type) and ar.role == self.role:
                    answer.append(ar)
        return answer
    
    def resources_for_agent(self, agent):
        answer = []
        for ar in agent.resources.all():
            if ar.resource_type.id == self.resource_type.id and ar.role == self.role:
                answer.append(ar)
            elif ar.resource_type.is_child_of(self.resource_type) and ar.role == self.role:
                answer.append(ar)
        return answer
    
    def agent_function_resources(self):
        answer = []
        function_agents = self.function.agents.all()
        for fa in function_agents:
            for ar in fa.function_resources.all():
                if ar.resource_type.id == self.resource_type.id and ar.role == self.role:
                    answer.append(ar)
                elif ar.resource_type.is_child_of(self.resource_type) and ar.role == self.role:
                    answer.append(ar)
        return answer
    
    def function_resources_for_agent(self, agent):
        answer = []
        af = agent.functions.filter(function=self.function)
        afrts = AgentFunctionResourceType.objects.filter(
            agent_function=af,
            role=self.role)
        for afrt in afrts:
            if afrt.resource_type.id == self.resource_type.id:
                answer.append(afrt)
            elif afrt.resource_type.is_child_of(self.resource_type):
                answer.append(afrt)
        return answer

    
class FunctionResourceFlow(models.Model):
    from_function = models.ForeignKey(EconomicFunction, related_name='outgoing_flows')
    to_function = models.ForeignKey(EconomicFunction, related_name='incoming_flows')
    resource_type = models.ForeignKey(EconomicResourceType, related_name='function_flows')
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal(0),
        help_text='If you enter Price and Quantity but not Value, Value will be computed as needed.')
    value = models.IntegerField(default=0)
    
    class Meta:
        ordering = ('from_function', 'to_function', 'resource_type',)
    
    def __unicode__(self):
        return " ".join(["from", self.from_function.name, "to", self.to_function.name, str(self.quantity), self.resource_type.name])
    
    def get_value(self):
        if self.value:
            return self.value
        if self.quantity and self.price:
            return int((self.quantity * self.price).quantize(Decimal('.01'), rounding=ROUND_UP))
        return 0

    
class EconomicAgent(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField( blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(default=0.0, blank=True, null=True)
    longitude = models.FloatField(default=0.0, blank=True, null=True)
    text_consumes = models.CharField(max_length=512, blank=True, null=True)
    text_produces = models.CharField(max_length=512, blank=True, null=True)
    text_info_provided_by = models.CharField(max_length=128, blank=True, null=True)
    text_contact = models.CharField(max_length=128, blank=True, null=True)
    text_degree_of_separation = models.CharField(max_length=128, blank=True, null=True)
    slug = models.SlugField("Page name", editable=False)
    
    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        unique_slugify(self, self.name)
        super(EconomicAgent, self).save(*args, **kwargs)

    @property
    def color(self):
        fns = self.functions.all()
        answer = 'grey'
        not_green = ""
        for fn in fns:
            if fn.color != 'green':
                not_green = fn.color
        if not_green:
            answer = not_green
        else:
            answer = 'green'
        return answer
           
        
    def address_is_editable(self):
        if self.communities.all().count()>1:
            return False
        else:
            return True
            
    def is_deletable(self):
        #import pdb; pdb.set_trace()
        if self.communities.all().count()>1 or self.clusters.all().count()>1:
            return False
        return True
        
    def is_removable(self, cluster):
        #import pdb; pdb.set_trace()
        if self.functions.all().count()>0 or self.resources.all().count()>0:
            return False
        return True
        
    def node_id(self):
        return "".join([ type(self).__name__, "-", self.slug])
    
    def inputs(self):
        return self.resources.filter(role="consumes")
    
    def outputs(self):
        return self.resources.filter(role="produces")
    
    def function_inputs(self, cluster):
        return AgentFunctionResourceType.objects.filter(
            agent_function__agent=self, 
            agent_function__function__cluster=cluster,
            role="consumes")
    
    def function_outputs(self, cluster):
        return AgentFunctionResourceType.objects.filter(
            agent_function__agent=self, 
            agent_function__function__cluster=cluster,
            role="produces")
    
    #def all_functions(self):
    #    return self.functions.all()
    
    def lat_lng(self):
        return ",".join([str(self.latitude), str(self.longitude)])

    

class CommunityAgent(models.Model):
    community = models.ForeignKey(Community, related_name="agents")
    agent = models.ForeignKey(EconomicAgent, related_name='communities')
    group = models.CharField(max_length=128, blank=True)
    geographic_area = models.CharField(max_length=255, blank=True)
    region_latitude = models.FloatField(default=0.0, blank=True, null=True)
    region_longitude = models.FloatField(default=0.0, blank=True, null=True)

    class Meta:
        ordering = ('community', 'agent')
    
    def __unicode__(self):
        return " ".join([self.community.name, self.agent.name])
        

class ClusterAgent(models.Model):
    cluster = models.ForeignKey(Cluster, related_name="cluster_agents")
    agent = models.ForeignKey(EconomicAgent, related_name='clusters')

    class Meta:
        ordering = ('cluster', 'agent')
    
    def __unicode__(self):
        return " ".join([self.cluster.name, self.agent.name])


class AgentFunction(models.Model):
    agent = models.ForeignKey(EconomicAgent, related_name='functions')
    function = models.ForeignKey(EconomicFunction, related_name='agents')
    
    class Meta:
        ordering = ('agent', 'function',)
    
    def __unicode__(self):
        return " ".join([self.agent.name, self.function.name])
    
    def save(self, *args, **kwargs):
        if not self.pk:
            community = self.function.cluster.community
            try:
                ca = CommunityAgent.objects.get(community=community, agent=self.agent)
            except CommunityAgent.DoesNotExist:
                ca = CommunityAgent(community=community, agent=self.agent).save()
        super(AgentFunction, self).save(*args, **kwargs)
        
    def node_id(self):
        return "".join([ type(self).__name__, "-", self.agent.name, self.function.name])
    
    def name(self):
        return self.agent.name
    
    @property
    def color(self):
        return self.function.color
    
    @property
    def cluster(self):
        return self.function.cluster
    
    def produced_function_resources(self):
        answer = []
        for afrt in self.function_resources.all():
            if afrt.role == "produces":
                answer.append(afrt)
        return answer
    
    def outputs(self):
        return self.function_resources.filter(role="produces")
    
    def inputs(self):
        return self.function_resources.filter(role="consumes")
    
    def flows(self):
        flows = list(self.incoming_flows.all())
        flows.extend(list(self.outgoing_flows.all()))
        return flows

class AgentResourceType(models.Model):
    agent = models.ForeignKey(EconomicAgent, related_name='resources')
    resource_type = models.ForeignKey(EconomicResourceType, related_name='agents')
    role = models.CharField(max_length=12, choices=ROLE_CHOICES)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal(0),
        help_text='If you enter Price and Quantity but not Value, Value will be computed as needed.')
    value = models.IntegerField(default=0)
    
    class Meta:
        ordering = ('agent', 'role', 'resource_type',)
    
    def __unicode__(self):
        return " ".join([self.agent.name, self.role, self.resource_type.name])
    
    def get_value(self):
        if self.value:
            return self.value
        if self.quantity and self.price:
            return int((self.quantity * self.price).quantize(Decimal('.01'), rounding=ROUND_UP))
        return 0
    

class AgentFunctionResourceType(models.Model):
    agent_function = models.ForeignKey(AgentFunction, related_name='function_resources')
    resource_type = models.ForeignKey(EconomicResourceType, related_name='agent_functions')
    role = models.CharField(max_length=12, choices=ROLE_CHOICES)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal(0),
        help_text='If you enter Price and Quantity but not Value, Value will be computed as needed.')
    value = models.IntegerField(default=0)
    
    class Meta:
        ordering = ('agent_function', 'role', 'resource_type',)
    
    def __unicode__(self):
        return " ".join([
            self.agent_function.agent.name,
            self.agent_function.function.name,
            self.role, 
            self.resource_type.name])
        
    def is_outlier(self):
        fn = self.agent_function.function
        resources = [frt.resource_type for frt in fn.resources.all()]
        if self.resource_type in resources:
            return False
        for r in resources:
            if self.resource_type.is_child_of(r):
                return False
        return True
    
    def get_value(self):
        if self.value:
            return self.value
        if self.quantity and self.price:
            return int((self.quantity * self.price).quantize(Decimal('.01'), rounding=ROUND_UP))
        return 0

    
class AgentResourceFlow(models.Model):
    from_function = models.ForeignKey(AgentFunction, related_name='outgoing_flows')
    to_function = models.ForeignKey(AgentFunction, related_name='incoming_flows')
    resource_type = models.ForeignKey(EconomicResourceType, related_name='agent_flows')
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal(0),
        help_text='If you enter Price and Quantity but not Value, Value will be computed as needed.')
    value = models.IntegerField(default=0)
    
    class Meta:
        ordering = ('from_function', 'to_function', 'resource_type',)
    
    def __unicode__(self):
        return " ".join([
            "from", 
            self.from_function.agent.name, 
            "to", 
            self.to_function.agent.name, 
            str(self.quantity), 
            self.resource_type.name])
        
    def get_value(self):
        if self.value:
            return self.value
        if self.quantity and self.price:
            return int((self.quantity * self.price).quantize(Decimal('.01'), rounding=ROUND_UP))
        return 0


class SiteSettings(models.Model):
    featured_cluster = models.ForeignKey(Cluster, related_name="featured")

   
def get_featured_cluster():
    try:
        ss = SiteSettings.objects.get(pk=1)
        return ss.featured_cluster
    except SiteSettings.DoesNotExist:
        return None
    
    
