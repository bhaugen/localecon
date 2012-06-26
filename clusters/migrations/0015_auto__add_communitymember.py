# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CommunityMember'
        db.create_table('clusters_communitymember', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('community', self.gf('django.db.models.fields.related.ForeignKey')(related_name='members', to=orm['clusters.Community'])),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(related_name='communities', to=orm['auth.User'])),
            ('permission_role', self.gf('django.db.models.fields.CharField')(max_length=12)),
        ))
        db.send_create_signal('clusters', ['CommunityMember'])


    def backwards(self, orm):
        
        # Deleting model 'CommunityMember'
        db.delete_table('clusters_communitymember')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'clusters.agentfunction': {
            'Meta': {'ordering': "('agent', 'function')", 'object_name': 'AgentFunction'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'functions'", 'to': "orm['clusters.EconomicAgent']"}),
            'function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'agents'", 'to': "orm['clusters.EconomicFunction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'clusters.agentfunctionresourcetype': {
            'Meta': {'ordering': "('agent_function', 'role', 'resource_type')", 'object_name': 'AgentFunctionResourceType'},
            'agent_function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'function_resources'", 'to': "orm['clusters.AgentFunction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'agent_functions'", 'to': "orm['clusters.EconomicResourceType']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'clusters.agentresourceflow': {
            'Meta': {'ordering': "('from_function', 'to_function', 'resource_type')", 'object_name': 'AgentResourceFlow'},
            'from_function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outgoing_flows'", 'to': "orm['clusters.AgentFunction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'agent_flows'", 'to': "orm['clusters.EconomicResourceType']"}),
            'to_function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incoming_flows'", 'to': "orm['clusters.AgentFunction']"}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'clusters.agentresourcetype': {
            'Meta': {'ordering': "('agent', 'role', 'resource_type')", 'object_name': 'AgentResourceType'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resources'", 'to': "orm['clusters.EconomicAgent']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'agents'", 'to': "orm['clusters.EconomicResourceType']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'clusters.cluster': {
            'Meta': {'object_name': 'Cluster'},
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'changed_cluster'", 'null': 'True', 'to': "orm['auth.User']"}),
            'community': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'clusters'", 'to': "orm['clusters.Community']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_cluster'", 'null': 'True', 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'function_aspect_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'root_function': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cluster_root'", 'null': 'True', 'to': "orm['clusters.EconomicFunction']"}),
            'root_resource': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cluster_root'", 'null': 'True', 'to': "orm['clusters.EconomicResourceType']"}),
            'sharing': ('django.db.models.fields.CharField', [], {'default': "'private'", 'max_length': '12'}),
            'when_changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'when_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'})
        },
        'clusters.community': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Community'},
            'agent_geographic_area_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'changed_community'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_community'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'map_center': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'map_zoom_level': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'resource_aspect_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'unit_of_value': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'community_units'", 'null': 'True', 'to': "orm['clusters.Unit']"}),
            'when_changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'when_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'})
        },
        'clusters.communityagent': {
            'Meta': {'ordering': "('community', 'agent')", 'object_name': 'CommunityAgent'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'communities'", 'to': "orm['clusters.EconomicAgent']"}),
            'community': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'agents'", 'to': "orm['clusters.Community']"}),
            'geographic_area': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'region_latitude': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'region_longitude': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'clusters.communitymember': {
            'Meta': {'object_name': 'CommunityMember'},
            'community': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'members'", 'to': "orm['clusters.Community']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'communities'", 'to': "orm['auth.User']"}),
            'permission_role': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        'clusters.communityresourcetype': {
            'Meta': {'ordering': "('community', 'resource_type')", 'object_name': 'CommunityResourceType'},
            'aspect': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'community': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resources'", 'to': "orm['clusters.Community']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'communities'", 'to': "orm['clusters.EconomicResourceType']"})
        },
        'clusters.economicagent': {
            'Meta': {'ordering': "('name',)", 'object_name': 'EconomicAgent'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'clusters.economicfunction': {
            'Meta': {'ordering': "('cluster', 'name')", 'object_name': 'EconomicFunction'},
            'aspect': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'functions'", 'to': "orm['clusters.Cluster']"}),
            'color': ('django.db.models.fields.CharField', [], {'default': "'green'", 'max_length': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'clusters.economicresourcetype': {
            'Meta': {'ordering': "('name',)", 'object_name': 'EconomicResourceType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['clusters.EconomicResourceType']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'unit_of_quantity': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resource_units'", 'null': 'True', 'to': "orm['clusters.Unit']"})
        },
        'clusters.functionresourceflow': {
            'Meta': {'ordering': "('from_function', 'to_function', 'resource_type')", 'object_name': 'FunctionResourceFlow'},
            'from_function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outgoing_flows'", 'to': "orm['clusters.EconomicFunction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'function_flows'", 'to': "orm['clusters.EconomicResourceType']"}),
            'to_function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incoming_flows'", 'to': "orm['clusters.EconomicFunction']"}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'clusters.functionresourcetype': {
            'Meta': {'ordering': "('function', 'role', 'resource_type')", 'object_name': 'FunctionResourceType'},
            'function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resources'", 'to': "orm['clusters.EconomicFunction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'functions'", 'to': "orm['clusters.EconomicResourceType']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'clusters.sitesettings': {
            'Meta': {'object_name': 'SiteSettings'},
            'featured_cluster': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'featured'", 'to': "orm['clusters.Cluster']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'clusters.unit': {
            'Meta': {'object_name': 'Unit'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['clusters']
