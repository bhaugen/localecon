import re
from django.template.defaultfilters import slugify

def split_thousands(n, sep=','):
    s = str(n)
    if len(s) <= 3: return s  
    return split_thousands(s[:-3], sep) + sep + s[-3:]

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

def graphify(cluster):
    fns = list(cluster.functions.all())
    rtypes = []
    for fn in fns:
        rtypes.extend([v.resource_type for v in fn.inputs()])
        rtypes.extend([v.resource_type for v in fn.outputs()])
    rtypes = list(set(rtypes))
    fns.extend(rtypes)
    return fns

def toposort(graph, queue):
    S = []
    while queue:
        u = queue.pop()
        S.append(u)
        for v in u.next:
            n = graph[graph.index(v)]
            n.preds.remove(u)
            if not n.preds:
                queue.append(n)
    return S
