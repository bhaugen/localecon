from django import template
from django.contrib.auth.models import User

from clusters.models import Cluster

register = template.Library()

class ClusterPermsNode(template.Node):
    def __init__(self, user_id, perm_name, cluster_id, varname):
        self.user_id = user_id
        self.perm_name = perm_name
        self.cluster_id = cluster_id
        self.varname = varname

    def render(self, context):
        user = User.objects.get(pk=self.user_id)
        cluster = Cluster.objects.get(pk=self.cluster_id)        
        context[self.varname] = cluster.permits(self.codename, user)
        return ''

def cluster_perms(parser, token):
    '''
    Template tag to check for permission against a cluster.

    Usage:
        {% load permissions %}

        {% for VARNAME in QUERYRESULT %}
            {% cluster_perms USER PERMNAME CLUSTER VARNAME as BOOLEANVARNAME %}
            {% if BOOLEANVARNAME %}
                I DO
            {% else %}
                I DON'T
            {% endif %}
            have permission for {{ VARNAME }}.{{ CODENAME }}!!
        {% endfor %}
    '''
    import pdb; pdb.set_trace()
    try:
        bits = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'tag requires exactly five arguments')
    if len(bits) != 6:
        raise template.TemplateSyntaxError(
            'tag requires exactly five arguments')
    if bits[4] != 'as':
        raise template.TemplateSyntaxError(
            "fourth argument to tag must be 'as'")
    return ClusterPermsNode(bits[1], bits[2], bits[3], bits[5])

cluster_perms = register.tag(cluster_perms)

