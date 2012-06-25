from django import template
from django.contrib.auth.models import User

from clusters.models import Cluster

register = template.Library()

class ClusterPermsNode(template.Node):
    def __init__(self, user, perm_name, cluster, varname):
        self.user = template.Variable(user)
        self.perm_name = perm_name
        self.cluster = template.Variable(cluster)
        self.varname = varname

    def render(self, context):
        #import pdb; pdb.set_trace()
        try:
            actual_user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        try:
            actual_cluster = self.cluster.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        answer = actual_cluster.permits(self.perm_name, actual_user)
        print actual_user, perm_name, actual_cluster, answer
        context[self.varname] = answer
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
    #import pdb; pdb.set_trace()
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

