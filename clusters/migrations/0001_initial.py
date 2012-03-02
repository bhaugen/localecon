# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Community'
        db.create_table('clusters_community', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('map_center', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
        ))
        db.send_create_signal('clusters', ['Community'])

        # Adding model 'Cluster'
        db.create_table('clusters_cluster', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('community', self.gf('django.db.models.fields.related.ForeignKey')(related_name='clusters', to=orm['clusters.Community'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('map_url', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('number_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('root_function', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='cluster_root', null=True, to=orm['clusters.EconomicFunction'])),
            ('root_resource', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='cluster_root', null=True, to=orm['clusters.EconomicResourceType'])),
        ))
        db.send_create_signal('clusters', ['Cluster'])

        # Adding model 'EconomicFunction'
        db.create_table('clusters_economicfunction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(related_name='functions', to=orm['clusters.Cluster'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('clusters', ['EconomicFunction'])

        # Adding model 'EconomicResourceType'
        db.create_table('clusters_economicresourcetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['clusters.EconomicResourceType'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('clusters', ['EconomicResourceType'])

        # Adding model 'CommunityResourceType'
        db.create_table('clusters_communityresourcetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('community', self.gf('django.db.models.fields.related.ForeignKey')(related_name='resources', to=orm['clusters.Community'])),
            ('resource_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='communities', to=orm['clusters.EconomicResourceType'])),
        ))
        db.send_create_signal('clusters', ['CommunityResourceType'])

        # Adding model 'FunctionResourceType'
        db.create_table('clusters_functionresourcetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('function', self.gf('django.db.models.fields.related.ForeignKey')(related_name='resources', to=orm['clusters.EconomicFunction'])),
            ('resource_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='functions', to=orm['clusters.EconomicResourceType'])),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('amount', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('clusters', ['FunctionResourceType'])

        # Adding model 'FunctionResourceFlow'
        db.create_table('clusters_functionresourceflow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_function', self.gf('django.db.models.fields.related.ForeignKey')(related_name='outgoing_flows', to=orm['clusters.EconomicFunction'])),
            ('to_function', self.gf('django.db.models.fields.related.ForeignKey')(related_name='incoming_flows', to=orm['clusters.EconomicFunction'])),
            ('resource_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='function_flows', to=orm['clusters.EconomicResourceType'])),
            ('amount', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('clusters', ['FunctionResourceFlow'])

        # Adding model 'EconomicAgent'
        db.create_table('clusters_economicagent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('clusters', ['EconomicAgent'])

        # Adding model 'CommunityAgent'
        db.create_table('clusters_communityagent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('community', self.gf('django.db.models.fields.related.ForeignKey')(related_name='agents', to=orm['clusters.Community'])),
            ('agent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='communities', to=orm['clusters.EconomicAgent'])),
        ))
        db.send_create_signal('clusters', ['CommunityAgent'])

        # Adding model 'AgentFunction'
        db.create_table('clusters_agentfunction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('agent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='functions', to=orm['clusters.EconomicAgent'])),
            ('function', self.gf('django.db.models.fields.related.ForeignKey')(related_name='agents', to=orm['clusters.EconomicFunction'])),
        ))
        db.send_create_signal('clusters', ['AgentFunction'])

        # Adding model 'AgentResourceType'
        db.create_table('clusters_agentresourcetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('agent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='resources', to=orm['clusters.EconomicAgent'])),
            ('resource_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='agents', to=orm['clusters.EconomicResourceType'])),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('amount', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('clusters', ['AgentResourceType'])

        # Adding model 'AgentResourceFlow'
        db.create_table('clusters_agentresourceflow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_function', self.gf('django.db.models.fields.related.ForeignKey')(related_name='outgoing_flows', to=orm['clusters.AgentFunction'])),
            ('to_function', self.gf('django.db.models.fields.related.ForeignKey')(related_name='incoming_flows', to=orm['clusters.AgentFunction'])),
            ('resource_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='agent_flows', to=orm['clusters.EconomicResourceType'])),
            ('amount', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('clusters', ['AgentResourceFlow'])

        # Adding model 'SiteSettings'
        db.create_table('clusters_sitesettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('featured_cluster', self.gf('django.db.models.fields.related.ForeignKey')(related_name='featured', to=orm['clusters.Cluster'])),
        ))
        db.send_create_signal('clusters', ['SiteSettings'])


    def backwards(self, orm):
        
        # Deleting model 'Community'
        db.delete_table('clusters_community')

        # Deleting model 'Cluster'
        db.delete_table('clusters_cluster')

        # Deleting model 'EconomicFunction'
        db.delete_table('clusters_economicfunction')

        # Deleting model 'EconomicResourceType'
        db.delete_table('clusters_economicresourcetype')

        # Deleting model 'CommunityResourceType'
        db.delete_table('clusters_communityresourcetype')

        # Deleting model 'FunctionResourceType'
        db.delete_table('clusters_functionresourcetype')

        # Deleting model 'FunctionResourceFlow'
        db.delete_table('clusters_functionresourceflow')

        # Deleting model 'EconomicAgent'
        db.delete_table('clusters_economicagent')

        # Deleting model 'CommunityAgent'
        db.delete_table('clusters_communityagent')

        # Deleting model 'AgentFunction'
        db.delete_table('clusters_agentfunction')

        # Deleting model 'AgentResourceType'
        db.delete_table('clusters_agentresourcetype')

        # Deleting model 'AgentResourceFlow'
        db.delete_table('clusters_agentresourceflow')

        # Deleting model 'SiteSettings'
        db.delete_table('clusters_sitesettings')


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
