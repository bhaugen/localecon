from django.db import models

from django.core.urlresolvers import reverse

from django.template.defaultfilters import slugify
import re
def unique_slugify(instance, value, slug_field_name='slug', queryset=None,
                   slug_separator='-'):
    """
    Calculates a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug. Chop its length down if we need to.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create a queryset, excluding the current instance.
    if not queryset:
        queryset = instance.__class__._default_manager.all()
        if instance.pk:
            queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '-%s' % next
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len-len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator=None):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
        value = re.sub('%s+' % re_sep, separator, value)
    return re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)

def nested_nodes(node, all_nodes):
     to_return = [node,]
     for subnode in all_nodes:
         if subnode.parent and subnode.parent.id == node.id:
             to_return.extend([nested_objects(subnode, all_nodes),])
     return to_return
 
def pair_list():
    pairlist = []
    for ef in EconomicFunction.objects.all():
        for inp in ef.inputs():
            pairlist.append((inp.resource_type, ef))
        for output in ef.outputs():
            pairlist.append((ef, output.resource_type))
    return pairlist
    
def parents_and_kids():
    pairlist = pair_list()
    children = {}
    for parent, child in pairlist:
        children.setdefault(parent, []).append(child)
    return children

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
    
    class Meta:
        verbose_name_plural = "communities"
        ordering = ('name',)
        
    def __unicode__(self):
        return self.name


class AggregateFunctionResource(object):
    def __init__(self, function, resource_type, role, quantity, value):
        self.function = function
        self.resource_type = resource_type
        self.role = role
        self.quantity = quantity
        self.value = value

   
class AgentGroupFlow(object):
    def __init__(self, from_function, to_function, resource_type, quantity, value):
        self.from_function = from_function
        self.to_function = to_function
        self.resource_type = resource_type
        self.quantity = quantity
        self.value = value

   
class AgentGroupFunction(object):
    def __init__(self, function, flow_dict):
        self.function = function
        self.flow_dict = flow_dict
        
    def flows(self):
        return self.flow_dict.values()
 

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
        
      

class Cluster(models.Model):
    community = models.ForeignKey(Community, related_name='clusters')
    name = models.CharField(max_length=128)
    description = models.TextField( blank=True, null=True)
    function_aspect_name = models.CharField(max_length=128, blank=True,
        help_text="Name for aspect fields on Economic Functions in this cluster.  If no name, aspects will not be used.")
    root_function = models.ForeignKey("EconomicFunction", blank=True, null=True,
        related_name="cluster_root", 
        help_text="Graph root is optional - can be either function or resource but not both")
    root_resource = models.ForeignKey("EconomicResourceType", blank=True, null=True,
        related_name="cluster_root", 
        help_text="Graph root is optional - can be either function or resource but not both")    
    
    def get_absolute_url(self):
        return ('cluster', (), {"cluster_id": self.id})
    
    def __unicode__(self):
        return " ".join([self.community.name, self.name])
    
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
        return list(set(answer))
      
    def agents(self):
        answer = []
        for fun in self.functions.all():
            for a in fun.agents.all():
                answer.append(a.agent)
        answer = list(set(answer))
        answer.sort(lambda x, y: cmp(x.name, y.name))
        return answer
    
    def disjoints(self):
        funs = self.functions.all().order_by("id")
        root = self.root_function
        if not root:
            if funs.count():
                root = funs[0]
        connected = connected_functions(root, funs, [])
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
                for og in fn.outgoing_flows.all():
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
                                af.function, afrt.resource_type, afrt.role, 0.0, 0.0)
                        rt = fn.resource_dict[reskey]
                        rt.quantity += afrt.quantity
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
                for af in afs:
                    if not af.function.id in grp.function_dict:
                        grp.function_dict[af.function.id] = AggregateFunction(
                            af.function, {})
                    fn = grp.function_dict[af.function.id]
                    for afrt in af.function_resources.all():
                        reskey = "".join([str(afrt.resource_type.id), afrt.role])
                        if not reskey in fn.resource_dict:
                            fn.resource_dict[reskey] = AggregateFunctionResource(
                                af.function, afrt.resource_type, afrt.role, 0.0, 0.0)
                        rt = fn.resource_dict[reskey]
                        rt.quantity += afrt.quantity
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
                                0.0, 0.0)
                        rt = fn.flow_dict[flowkey]
                        rt.quantity += flow.quantity
                        rt.value += flow.value
        group_flows = []
        for grp in groups.values():
            for fn in grp.all_functions():
                group_flows.extend(fn.flows())
        return group_flows


class EconomicFunction(models.Model):
    cluster = models.ForeignKey(Cluster, related_name="functions")
    name = models.CharField(max_length=128)
    aspect = models.CharField(max_length=128, blank=True)
    slug = models.SlugField("Page name", editable=False)
    
    class Meta:
        ordering = ('cluster', 'name',)
    
    def __unicode__(self):
        return " ".join([self.cluster.name, self.name])
    
    def save(self, *args, **kwargs):
        unique_slugify(self, self.name)
        super(EconomicFunction, self).save(*args, **kwargs)
        
    def node_id(self):
        return "".join([ type(self).__name__, "-", self.slug])
    
    def inputs(self):
        return self.resources.filter(role="consumes")
    
    def outputs(self):
        return self.resources.filter(role="produces")
    
    def from_nodes(self, cluster):
        # cluster is here only for duck typing
        # with EconomicResourceTypes
        return [v.resource_type for v in self.inputs()]
    
    def to_nodes(self, cluster):
        return [v.resource_type for v in self.outputs()]

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
    value = models.IntegerField(default=0)
    
    class Meta:
        ordering = ('from_function', 'to_function', 'resource_type',)
    
    def __unicode__(self):
        return " ".join(["from", self.from_function.name, "to", self.to_function.name, str(self.quantity), self.resource_type.name])

    
class EconomicAgent(models.Model):
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(default=0.0, blank=True, null=True)
    longitude = models.FloatField(default=0.0, blank=True, null=True)
    slug = models.SlugField("Page name", editable=False)
    
    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        unique_slugify(self, self.name)
        super(EconomicAgent, self).save(*args, **kwargs)
        
    def address_is_editable(self):
        if self.communities.all().count()>1:
            return False
        else:
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

class AgentResourceType(models.Model):
    agent = models.ForeignKey(EconomicAgent, related_name='resources')
    resource_type = models.ForeignKey(EconomicResourceType, related_name='agents')
    role = models.CharField(max_length=12, choices=ROLE_CHOICES)
    quantity = models.IntegerField(default=0)
    value = models.IntegerField(default=0)
    
    class Meta:
        ordering = ('agent', 'role', 'resource_type',)
    
    def __unicode__(self):
        return " ".join([self.agent.name, self.role, self.resource_type.name])
    

class AgentFunctionResourceType(models.Model):
    agent_function = models.ForeignKey(AgentFunction, related_name='function_resources')
    resource_type = models.ForeignKey(EconomicResourceType, related_name='agent_functions')
    role = models.CharField(max_length=12, choices=ROLE_CHOICES)
    quantity = models.IntegerField(default=0)
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

    
class AgentResourceFlow(models.Model):
    from_function = models.ForeignKey(AgentFunction, related_name='outgoing_flows')
    to_function = models.ForeignKey(AgentFunction, related_name='incoming_flows')
    resource_type = models.ForeignKey(EconomicResourceType, related_name='agent_flows')
    quantity = models.IntegerField(default=0)
    value = models.IntegerField(default=0)
    
    class Meta:
        ordering = ('from_function', 'to_function', 'resource_type',)
    
    def __unicode__(self):
        return " ".join(["from", self.from_function.agent.name, "to", self.to_function.agent.name, str(self.quantity), self.resource_type.name])


class SiteSettings(models.Model):
    featured_cluster = models.ForeignKey(Cluster, related_name="featured")

   
def get_featured_cluster():
    try:
        ss = SiteSettings.objects.get(pk=1)
        return ss.featured_cluster
    except SiteSettings.DoesNotExist:
        return None
    
    
