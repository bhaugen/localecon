# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Unit'
        db.create_table('clusters_unit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('abbrev', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('symbol', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
        ))
        db.send_create_signal('clusters', ['Unit'])

        # Adding field 'Community.unit_of_value'
        db.add_column('clusters_community', 'unit_of_value', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='community_units', null=True, to=orm['clusters.Unit']), keep_default=False)

        # Adding field 'AgentResourceFlow.value'
        db.add_column('clusters_agentresourceflow', 'value', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'FunctionResourceType.value'
        db.add_column('clusters_functionresourcetype', 'value', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'FunctionResourceFlow.value'
        db.add_column('clusters_functionresourceflow', 'value', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'EconomicResourceType.unit_of_quantity'
        db.add_column('clusters_economicresourcetype', 'unit_of_quantity', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='resource_units', null=True, to=orm['clusters.Unit']), keep_default=False)

        # Adding field 'AgentResourceType.value'
        db.add_column('clusters_agentresourcetype', 'value', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'Unit'
        db.delete_table('clusters_unit')

        # Deleting field 'Community.unit_of_value'
        db.delete_column('clusters_community', 'unit_of_value_id')

        # Deleting field 'AgentResourceFlow.value'
        db.delete_column('clusters_agentresourceflow', 'value')

        # Deleting field 'FunctionResourceType.value'
        db.delete_column('clusters_functionresourcetype', 'value')

        # Deleting field 'FunctionResourceFlow.value'
        db.delete_column('clusters_functionresourceflow', 'value')

        # Deleting field 'EconomicResourceType.unit_of_quantity'
        db.delete_column('clusters_economicresourcetype', 'unit_of_quantity_id')

        # Deleting field 'AgentResourceType.value'
        db.delete_column('clusters_agentresourcetype', 'value')


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
            'to_function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incoming_flows'", 'to': "orm['clusters.AgentFunction']"}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'clusters.agentresourcetype': {
            'Meta': {'ordering': "('agent', 'role', 'resource_type')", 'object_name': 'AgentResourceType'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resources'", 'to': "orm['clusters.EconomicAgent']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'agents'", 'to': "orm['clusters.EconomicResourceType']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'unit_of_value': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'community_units'", 'null': 'True', 'to': "orm['clusters.Unit']"})
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
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'unit_of_quantity': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resource_units'", 'null': 'True', 'to': "orm['clusters.Unit']"})
        },
        'clusters.functionresourceflow': {
            'Meta': {'ordering': "('from_function', 'to_function', 'resource_type')", 'object_name': 'FunctionResourceFlow'},
            'from_function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outgoing_flows'", 'to': "orm['clusters.EconomicFunction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'function_flows'", 'to': "orm['clusters.EconomicResourceType']"}),
            'to_function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incoming_flows'", 'to': "orm['clusters.EconomicFunction']"}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'clusters.functionresourcetype': {
            'Meta': {'ordering': "('function', 'role', 'resource_type')", 'object_name': 'FunctionResourceType'},
            'function': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resources'", 'to': "orm['clusters.EconomicFunction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
        }
    }

    complete_apps = ['clusters']
