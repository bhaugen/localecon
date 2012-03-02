# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'AgentResourceFlow.amount'
        #db.delete_column('clusters_agentresourceflow', 'amount')

        # Adding field 'AgentResourceFlow.quantity'
        #db.add_column('clusters_agentresourceflow', 'quantity', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Renaming field 'AgentResourceFlow.amount'
        db.rename_column('clusters_agentresourceflow', 'amount', 'quantity')

        # Deleting field 'FunctionResourceType.amount'
        #db.delete_column('clusters_functionresourcetype', 'amount')

        # Adding field 'FunctionResourceType.quantity'
        #db.add_column('clusters_functionresourcetype', 'quantity', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Renaming field 'FunctionResourceType.amount'
        db.rename_column('clusters_functionresourcetype', 'amount', 'quantity')

        # Deleting field 'FunctionResourceFlow.amount'
        #db.delete_column('clusters_functionresourceflow', 'amount')

        # Adding field 'FunctionResourceFlow.quantity'
        #db.add_column('clusters_functionresourceflow', 'quantity', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Renaming field 'FunctionResourceFlow.amount'
        db.rename_column('clusters_functionresourceflow', 'amount', 'quantity')

        # Deleting field 'AgentResourceType.amount'
        #db.delete_column('clusters_agentresourcetype', 'amount')

        # Adding field 'AgentResourceType.quantity'
        #db.add_column('clusters_agentresourcetype', 'quantity', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Renaming field 'AgentResourceType.amount'
        db.rename_column('clusters_agentresourcetype', 'amount', 'quantity')


    def backwards(self, orm):
        
        # Adding field 'AgentResourceFlow.amount'
        #db.add_column('clusters_agentresourceflow', 'amount', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Deleting field 'AgentResourceFlow.quantity'
        #db.delete_column('clusters_agentresourceflow', 'quantity')
        
        # Renaming field 'AgentResourceFlow.quantity'
        db.rename_column('clusters_agentresourceflow', 'quantity', 'amount')

        # Adding field 'FunctionResourceType.amount'
        #db.add_column('clusters_functionresourcetype', 'amount', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Deleting field 'FunctionResourceType.quantity'
        #db.delete_column('clusters_functionresourcetype', 'quantity')
        
        # Renaming field 'FunctionResourceType.quantity'
        db.rename_column('clusters_functionresourcetype', 'quantity', 'amount')

        # Adding field 'FunctionResourceFlow.amount'
        #db.add_column('clusters_functionresourceflow', 'amount', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Deleting field 'FunctionResourceFlow.quantity'
        #db.delete_column('clusters_functionresourceflow', 'quantity')
        
        # Renaming field 'FunctionResourceFlow.quantity'
        db.rename_column('clusters_functionresourceflow', 'quantity', 'amount')

        # Adding field 'AgentResourceType.amount'
        #db.add_column('clusters_agentresourcetype', 'amount', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Deleting field 'AgentResourceType.quantity'
        #db.delete_column('clusters_agentresourcetype', 'quantity')
        
        # Renaming field 'AgentResourceType.quantity'
        db.rename_column('clusters_agentresourcetype', 'quantity', 'amount')


    models = {
        'clusters.agentfunction': {
            'Meta': {'ordering': "('agent', 'function')", 'object_name': 'AgentFunction'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'functions'", 'to': "orm['clusters.EconomicAgent']"}),
            'function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'agents'", 'to': "orm['clusters.EconomicFunction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'clusters.agentresourceflow': {
            'Meta': {'ordering': "('from_function', 'to_function', 'resource_type')", 'object_name': 'AgentResourceFlow'},
            'from_function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outgoing_flows'", 'to': "orm['clusters.AgentFunction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'agent_flows'", 'to': "orm['clusters.EconomicResourceType']"}),
            'to_function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incoming_flows'", 'to': "orm['clusters.AgentFunction']"})
        },
        'clusters.agentresourcetype': {
            'Meta': {'ordering': "('agent', 'role', 'resource_type')", 'object_name': 'AgentResourceType'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resources'", 'to': "orm['clusters.EconomicAgent']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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
            'from_function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outgoing_flows'", 'to': "orm['clusters.EconomicFunction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'function_flows'", 'to': "orm['clusters.EconomicResourceType']"}),
            'to_function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incoming_flows'", 'to': "orm['clusters.EconomicFunction']"})
        },
        'clusters.functionresourcetype': {
            'Meta': {'ordering': "('function', 'role', 'resource_type')", 'object_name': 'FunctionResourceType'},
            'function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resources'", 'to': "orm['clusters.EconomicFunction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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
