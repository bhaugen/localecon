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

def function_resource_table(cluster):
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
        functions[fr.function][row_cell] = fr.amount * mult
        functions[fr.function][col_count + 1] += fr.amount * mult
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
    
    
class Community(models.Model):
    name = models.CharField(max_length=128)
    map_center = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(default=0.0, blank=True, null=True, editable=False)
    longitude = models.FloatField(default=0.0, blank=True, null=True, editable=False)
    
    class Meta:
        verbose_name_plural = "communities"
        ordering = ('name',)
        
    def __unicode__(self):
        return self.name
      

class Cluster(models.Model):
    community = models.ForeignKey(Community, related_name='clusters')
    name = models.CharField(max_length=128)
    description = models.TextField( blank=True, null=True)
    map_url = models.CharField(max_length=255, blank=True)
    number_description = models.TextField( blank=True, null=True,
        help_text="This description will appear on tables with numbers, to tell what the numbers mean.")
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
        return list(set(answer))
      
      
    def agents(self):
        answer = []
        for fun in self.functions.all():
            for a in fun.agents.all():
                answer.append(a.agent)
        answer = list(set(answer))
        answer.sort(lambda x, y: cmp(x.name, y.name))
        return answer

class EconomicFunction(models.Model):
    cluster = models.ForeignKey(Cluster, related_name="functions")
    name = models.CharField(max_length=128)
    slug = models.SlugField("Page name", editable=False)
    
    class Meta:
        ordering = ('cluster', 'name',)
    
    def __unicode__(self):
        return " ".join([self.cluster.name, self.name])
    
    def save(self, force_insert=False, force_update=False):
        unique_slugify(self, self.name)
        super(EconomicFunction, self).save(force_insert, force_update)
        
    def node_id(self):
        return "".join([ type(self).__name__, "-", self.slug])
    
    def inputs(self):
        return self.resources.filter(role="consumes")
    
    def outputs(self):
        return self.resources.filter(role="produces")

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
    
    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return self.name
    
    def save(self, force_insert=False, force_update=False):
        unique_slugify(self, self.name)
        super(EconomicResourceType, self).save(force_insert, force_update)
        
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
    
    def is_child_of(self, resource_type):
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
    amount = models.IntegerField(default=0)
    
    class Meta:
        ordering = ('function', 'role', 'resource_type',)
    
    def __unicode__(self):
        return " ".join([self.function.name, self.role, self.resource_type.name])
    
    def save(self, force_insert=False, force_update=False):
        if not self.pk:
            community = self.function.cluster.community
            rt = self.resource_type
            try:
                crt = CommunityResourceType.objects.get(community=community, resource_type=rt)
            except CommunityResourceType.DoesNotExist:
                crt = CommunityResourceType(community=community, resource_type=rt).save()
        super(FunctionResourceType, self).save(force_insert, force_update)
        
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

    
class EconomicAgent(models.Model):
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(default=0.0, blank=True, null=True, editable=False)
    longitude = models.FloatField(default=0.0, blank=True, null=True, editable=False)
    slug = models.SlugField("Page name", editable=False)
    
    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return self.name
    
    def save(self, force_insert=False, force_update=False):
        unique_slugify(self, self.name)
        super(EconomicAgent, self).save(force_insert, force_update)
        
    def node_id(self):
        return "".join([ type(self).__name__, "-", self.slug])
    


class CommunityAgent(models.Model):
    community = models.ForeignKey(Community, related_name="agents")
    agent = models.ForeignKey(EconomicAgent, related_name='communities')

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
    
    def save(self, force_insert=False, force_update=False):
        if not self.pk:
            community = self.function.cluster.community
            try:
                ca = CommunityAgent.objects.get(community=community, agent=self.agent)
            except CommunityAgent.DoesNotExist:
                ca = CommunityAgent(community=community, agent=self.agent).save()
        super(AgentFunction, self).save(force_insert, force_update)


class AgentResourceType(models.Model):
    agent = models.ForeignKey(EconomicAgent, related_name='resources')
    resource_type = models.ForeignKey(EconomicResourceType, related_name='agents')
    role = models.CharField(max_length=12, choices=ROLE_CHOICES)
    amount = models.IntegerField(default=0)
    
    class Meta:
        ordering = ('agent', 'role', 'resource_type',)
    
    def __unicode__(self):
        return " ".join([self.agent.name, self.role, self.resource_type.name])
    

class SiteSettings(models.Model):
    featured_cluster = models.ForeignKey(Cluster, related_name="featured")

   
def get_featured_cluster():
    try:
        ss = SiteSettings.objects.get(pk=1)
        return ss.featured_cluster
    except SiteSettings.DoesNotExist:
        return None
    
    