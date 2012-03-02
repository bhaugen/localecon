# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Community.map_zoom_level'
        db.add_column('clusters_community', 'map_zoom_level', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Community.map_zoom_level'
        db.delete_column('clusters_community', 'map_zoom_level')


    models = {
        'clusters.agentfunction': {
            'Meta': {'ordering': "('agent', 'function')", 'object_name': 'AgentFunction'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'functions'", 'to': "orm['clusters.EconomicAgent']"}),
            'function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'agents'", 'to': "orm['clusters.EconomicFunction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'clusters.agentresourceflow': {
            'Meta': {'ordering': "('from_function', 'to_function', 'resource_type')", 'object_name': 'AgentResourceFlow'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'from_function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outgoing_flows'", 'to': "orm['clusters.AgentFunction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'agent_flows'", 'to': "orm['clusters.EconomicResourceType']"}),
            'to_function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incoming_flows'", 'to': "orm['clusters.AgentFunction']"})
        },
        'clusters.agentresourcetype': {
            'Meta': {'ordering': "('agent', 'role', 'resource_type')", 'object_name': 'AgentResourceType'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resources'", 'to': "orm['clusters.EconomicAgent']"}),
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'agents'", 'to': "orm['clusters.EconomicResourceType']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        'clusters.cluster': {
            'Meta': {'object_name': 'Cluster'},
            'community': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'clusters'", 'to': "orm['clusters.Community']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'number_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'root_function': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cluster_root'", 'null': 'True', 'to': "orm['clusters.EconomicFunction']"}),
            'root_resource': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cluster_root'", 'null': 'True', 'to': "orm['clusters.EconomicResourceType']"})
        },
        'clusters.community': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Community'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'map_center': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'map_zoom_level': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'clusters.communityagent': {
            'Meta': {'ordering': "('community', 'agent')", 'object_name': 'CommunityAgent'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'communities'", 'to': "orm['clusters.EconomicAgent']"}),
            'community': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'agents'", 'to': "orm['clusters.Community']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'clusters.communityresourcetype': {
            'Meta': {'ordering': "('community', 'resource_type')", 'object_name': 'CommunityResourceType'},
            'community': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resources'", 'to': "orm['clusters.Community']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'communities'", 'to': "orm['clusters.EconomicResourceType']"})
        },
        'clusters.economicagent': {
            'Meta': {'ordering': "('name',)", 'object_name': 'EconomicAgent'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'clusters.economicfunction': {
            'Meta': {'ordering': "('cluster', 'name')", 'object_name': 'EconomicFunction'},
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'functions'", 'to': "orm['clusters.Cluster']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'clusters.economicresourcetype': {
            'Meta': {'ordering': "('name',)", 'object_name': 'EconomicResourceType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['clusters.EconomicResourceType']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'clusters.functionresourceflow': {
            'Meta': {'ordering': "('from_function', 'to_function', 'resource_type')", 'object_name': 'FunctionResourceFlow'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'from_function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outgoing_flows'", 'to': "orm['clusters.EconomicFunction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'function_flows'", 'to': "orm['clusters.EconomicResourceType']"}),
            'to_function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incoming_flows'", 'to': "orm['clusters.EconomicFunction']"})
        },
        'clusters.functionresourcetype': {
            'Meta': {'ordering': "('function', 'role', 'resource_type')", 'object_name': 'FunctionResourceType'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resources'", 'to': "orm['clusters.EconomicFunction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'functions'", 'to': "orm['clusters.EconomicResourceType']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        'clusters.sitesettings': {
            'Meta': {'object_name': 'SiteSettings'},
            'featured_cluster': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'featured'", 'to': "orm['clusters.Cluster']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['clusters']
