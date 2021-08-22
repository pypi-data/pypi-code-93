from sqlpie.client import Sqlpie
from sqlpie.dynamic_env import DynamicEnv
import unittest
from unittest.mock import MagicMock
import copy

example_model_client = Sqlpie(models=['example_model'], vars_payload={"example_model": {"test_var": "some_value"}})
example_model = example_model_client.models['example_model']
model_with_custom_prep_schema = Sqlpie(models=['model_2']).models['model_2']
dynamic_env = Sqlpie(vars_payload={"dynamic_env": "new_version"})
excludes = Sqlpie(excludes=['model_2'])

all_models = Sqlpie()
all_models_with_payload = Sqlpie(vars_payload={"example_model": {"test_var": "some_value"}})
de_test_diff_models = Sqlpie()
diff_query=de_test_diff_models.api_data['models']['model_2']['rendered_model']['custom_prep_schema.enrich_example_1']['rendered_query']
de_test_diff_models.api_data['models']['model_2']['rendered_model']['custom_prep_schema.enrich_example_1']['rendered_query'] = diff_query + 'XXXX'
full_dynamic_env = DynamicEnv(dynamic_env='test', prod_version=all_models.api_data['models'], branch_version=de_test_diff_models.api_data['models'])
#test_custom_prep_schema.enrich_example_1
class TestClient(unittest.TestCase):
  maxDiff = None
  def test_dag_validity_for_single_model(self):
    self.assertEqual(example_model.dag.validate()[0], True)

  def test_ind_nodes(self):
    self.assertEqual(example_model.dag.ind_nodes(),  ['example_source_schema.table_1', 'example_source_schema.table_2', 'example_source_schema.table_3'])
  
  def test_all_leaves(self):
    self.assertEqual(example_model.dag.all_leaves(),  ['example_model.example_3'])
  
  def test_model_key_names(self):
    self.assertEqual(list(example_model.rendered_model.keys()), ['example_model.example_3', 'example_model.example_2', 'example_model_prep.example_1'])

  def test_custom_prep_schema(self):
    self.assertEqual(model_with_custom_prep_schema.prep_model, 'custom_prep_schema')

  def test_snippets_rendering(self):
    rendered_query = example_model.rendered_model['example_model_prep.example_1']['rendered_query']
    query = "\nselect *, date_trunc('month', CONVERT_TIMEZONE ('UTC', 'America/New_York', getdate()))::date\nfrom  example_source_schema_public.table_1 table_1\njoin  example_source_schema_public.table_2 table_2\non table_1.id = table_2.id\njoin  example_source_schema_public.table_3 table_3\non table_2.table_3_id = table_3.id"
    self.assertEqual(rendered_query, query)

  def test_vars_rendering_single_model(self):
    rendered_query = example_model.rendered_model['example_model.example_2']['rendered_query']
    query = "\nselect *, 'some_value'\nfrom  example_model_prep.example_1"
    self.assertEqual(rendered_query, query)

  def test_vars_rendering_all_models(self):
    rendered_query = all_models_with_payload.models['example_model'].rendered_model['example_model.example_2']['rendered_query']
    query = "\nselect *, 'some_value'\nfrom  example_model_prep.example_1"
    self.assertEqual(rendered_query, query)

  def test_model_names_extraction(self):
    self.assertEqual(example_model.all_models, ['model_2', 'model_with_empty_config', 'example_model'])

  def test_destination_schemas(self):
    destinations  = ['custom_prep_schema', 'model_with_empty_config', 'example_model_prep']
    models = list(all_models.models.values())
    output_destinations = list(map(lambda model: model._execution_metadata['destination_schema'], models))
    self.assertEqual(destinations, output_destinations)
  
  def test_dag_validity_for_all_models_1(self):
    self.assertEqual(all_models.models['example_model'].dag.validate()[0], True)

  def test_dag_validity_for_all_models_2(self):
    self.assertEqual(all_models.models['model_2'].dag.validate()[0], True)

  def test_excluding(self):
    self.assertEqual(excludes.api_data['selected_models'], ['model_with_empty_config', 'example_model'])

  def test_model_api_data_keys(self):
    keys = [
            'ind_nodes',
            'all_leaves',
            'graph_object',
            'dag_topological_sort',
            'dag_index',
            'prep_model',
            'sources',
            'rendered_model',
            'viz_data'
            ]
    self.assertEqual( list(all_models.api_data['models']['example_model'].keys()) , keys)

  def test_dag_index_structure(self):
    dag_index = {'example_source_schema.table_1': {'predecessors': [], 'downstreams': ['example_model_prep.example_1']}, 'example_source_schema.table_2': {'predecessors': [], 'downstreams': ['example_model_prep.example_1']}, 'example_source_schema.table_3': {'predecessors': [], 'downstreams': ['example_model_prep.example_1']}, 'example_model_prep.example_1': {'predecessors': ['example_source_schema.table_1', 'example_source_schema.table_2', 'example_source_schema.table_3'], 'downstreams': ['example_model.example_2', 'example_model.example_3']}, 'example_model.example_2': {'predecessors': ['example_model_prep.example_1'], 'downstreams': ['example_model.example_3']}, 'example_model.example_3': {'predecessors': ['example_model.example_2', 'example_model_prep.example_1'], 'downstreams': []}}
    self.assertEqual(all_models.api_data['models']['example_model']['dag_index'], dag_index)
  
  def test_all_models_edges(self):
    output_edges = sorted(all_models.dag_edges)
    edges = sorted([['custom_prep_schema.enrich_example_1', 'model_2.example_1'], ['example_model.example_2', 'custom_prep_schema.enrich_example_1'], ['example_model.example_2', 'example_model.example_3'], ['example_model.example_3', 'model_2.example_1'], ['example_model_prep.example_1', 'example_model.example_2'], ['example_model_prep.example_1', 'example_model.example_3'], ['example_model_prep.example_1', 'model_2.example_1'], ['example_source_schema.table_1', 'example_model_prep.example_1'], ['example_source_schema.table_1', 'model_with_empty_config.query_1'], ['example_source_schema.table_2', 'example_model_prep.example_1'], ['example_source_schema.table_3', 'custom_prep_schema.enrich_example_1'], ['example_source_schema.table_3', 'example_model_prep.example_1']])
    self.assertEqual(output_edges, edges)

  def test_single_model_edges(self):
    output_edges = sorted(example_model_client.dag_edges)
    edges = sorted([['example_source_schema.table_1', 'example_model_prep.example_1'], ['example_source_schema.table_2', 'example_model_prep.example_1'], ['example_model_prep.example_1', 'example_model.example_3'], ['example_model_prep.example_1', 'example_model.example_2']])

  def test_api_data_structure(self):
    api_data_keys_output = list(all_models.api_data.keys())
    api_data_keys = ['models', 'selected_models', 'dag', 'table_index', 'file_path_index']
    self.assertEqual(api_data_keys_output, api_data_keys)

  def test_dag_api_data(self):
    dag_api_data_keys_output = list(all_models.api_data['dag'].keys())
    dag_api_data_keys = ['ind_nodes', 'all_leaves', 'graph_object', 'dag_topological_sort', 'dag_index', 'viz_data']
    self.assertEqual(dag_api_data_keys_output, dag_api_data_keys)
  
  def test_table_index_output(self):
    table_index = {'model_2.example_1': {'file_path': './models/model_2/example_1.sql', 'source_name': 'model_2', 'schema': 'model_2', 'table_name': 'model_2.example_1', 'table_short_name': 'example_1', 'update_method': 'append', 'source_type': 'model'}, 'custom_prep_schema.enrich_example_1': {'file_path': './models/model_2/enrich_example_1.sql', 'source_name': 'model_2', 'schema': 'custom_prep_schema', 'table_name': 'custom_prep_schema.enrich_example_1', 'table_short_name': 'enrich_example_1', 'update_method': 'append', 'source_type': 'prep', 'included_in': ['model_2']}, 'model_with_empty_config.query_1': {'file_path': './models/model_with_empty_config/query_1.sql', 'source_name': 'model_with_empty_config', 'schema': 'model_with_empty_config', 'table_name': 'model_with_empty_config.query_1', 'table_short_name': 'query_1', 'update_method': 'append', 'source_type': 'model'}, 'example_model.example_3': {'file_path': './models/example_model/example_3.sql', 'source_name': 'example_model', 'schema': 'example_model', 'table_name': 'example_model.example_3', 'table_short_name': 'example_3', 'update_method': 'append', 'description': 'monthly aggregation view', 'source_type': 'model', 'included_in': ['model_2']}, 'example_model.example_2': {'file_path': './models/example_model/example_2.sql', 'source_name': 'example_model', 'schema': 'example_model', 'table_name': 'example_model.example_2', 'table_short_name': 'example_2', 'update_method': 'append', 'description': 'daily aggregation view', 'source_type': 'model', 'included_in': ['model_2']}, 'example_model_prep.example_1': {'file_path': './models/example_model/example_1_prep.sql', 'source_name': 'example_model', 'schema': 'example_model_prep', 'table_name': 'example_model_prep.example_1', 'table_short_name': 'example_1', 'update_method': 'append', 'description': 'reads data from sources and performs some processing and enrichment', 'source_type': 'prep', 'included_in': ['model_2', 'example_model']}, 'example_source_schema.table_3': {'source_type': 'source', 'source_name': 'example_source_schema', 'schema': 'example_source_schema_public', 'table_name': 'example_source_schema.table_3', 'table_short_name': 'table_3', 'destination_table': 'custom_prep_schema.enrich_example_1', 'included_in': ['model_2', 'example_model'], 'description': 'bing ads daily aggregated metrics'}, 'example_source_schema.table_1': {'source_type': 'source', 'source_name': 'example_source_schema', 'schema': 'example_source_schema_public', 'table_name': 'example_source_schema.table_1', 'table_short_name': 'table_1', 'destination_table': 'model_with_empty_config.query_1', 'included_in': ['model_with_empty_config', 'example_model'], 'description': 'facebook advertsing daily aggregated metrics'}, 'example_source_schema.table_2': {'source_type': 'source', 'source_name': 'example_source_schema', 'schema': 'example_source_schema_public', 'table_name': 'example_source_schema.table_2', 'table_short_name': 'table_2', 'destination_table': 'example_model_prep.example_1', 'included_in': ['example_model'], 'description': 'google adwords daily aggregated metrics'}}
    table_index_output = all_models.api_data['table_index']
    self.assertEqual(table_index, table_index_output)

  def test_table_index_included_in(self):
    table_3_included_in_output  = all_models.api_data['table_index']['example_source_schema.table_3']['included_in']
    table_3_included_in = ['model_2', 'example_model']
    self.assertEqual(table_3_included_in, table_3_included_in_output)
 
  def test_table_index_model_description(self):
    description_output = all_models.api_data['table_index']['example_model_prep.example_1']['description']
    description = 'reads data from sources and performs some processing and enrichment'
    self.assertEqual(description_output, description)

  def test_table_index_source_description(self):
    description_output = all_models.api_data['table_index']['example_source_schema.table_1']['description']
    description = 'facebook advertsing daily aggregated metrics'
    self.assertEqual(description_output, description)

  def test_prep_source_type(self):
    prep_source_type = all_models.api_data['table_index']['example_model_prep.example_1']['source_type']
    self.assertEqual(prep_source_type, 'prep')

  def test_prep_source_type_for_dynamic_env(self):
    prep_source_type = dynamic_env.api_data['table_index']['new_version_example_model_prep.example_1']['source_type']
    self.assertEqual(prep_source_type, 'prep')

  def test_dynamic_env_table_index_source_name_for_prep(self):
    prep_source_name = dynamic_env.api_data['table_index']['new_version_example_model_prep.example_1']['source_name']
    self.assertEqual(prep_source_name, 'new_version_example_model')
  
  def test_prep_model_inclusion(self):
    included_in_output = all_models.api_data['table_index']['example_model_prep.example_1']['included_in']
    included_in = ['model_2','example_model']
    self.assertEqual(included_in_output, included_in)

  def test_file_path_index(self):
    file_path_index = {'./models/model_2/example_1.sql': 'model_2.example_1', './models/model_2/enrich_example_1.sql': 'custom_prep_schema.enrich_example_1', './models/model_with_empty_config/query_1.sql': 'model_with_empty_config.query_1', './models/example_model/example_3.sql': 'example_model.example_3', './models/example_model/example_1_prep.sql': 'example_model_prep.example_1', './models/example_model/example_2.sql': 'example_model.example_2'}
    file_path_index_output = all_models.api_data['file_path_index']
    self.assertEqual(file_path_index, file_path_index_output)
  
  def test_dynamic_env_var_is_changing_prod_model_names(self):
    self.assertEqual(list(dynamic_env.models.keys()), ['new_version_model_2', 'new_version_model_with_empty_config', 'new_version_example_model'])

  def test_dynamic_env_model_names(self):
    models = list(dynamic_env.models.values())
    list(map(lambda model: model.dynamic_env_model, models))
    self.assertEqual(list(map(lambda model: model.dynamic_env_model, models)),['new_version_model_2', 'new_version_model_with_empty_config', 'new_version_example_model'])

  def test_dynamic_env_is_setting_destination_schema_to_new_env(self):
    models = list(dynamic_env.models.values())
    destinations  = ['new_version_custom_prep_schema', 'new_version_model_with_empty_config', 'new_version_example_model_prep']
    output_destinations = list(map(lambda model: model._execution_metadata['destination_schema'], models))
    self.assertEqual(destinations, output_destinations)

  def test_dynamic_env_var_is_rendering_all_tables_names_with_the_version_prefix(self):
    self.assertEqual(list(dynamic_env.api_data['table_index'].keys()), ['new_version_model_2.example_1', 'new_version_custom_prep_schema.enrich_example_1', 'new_version_model_with_empty_config.query_1', 'new_version_example_model.example_3', 'new_version_example_model.example_2', 'new_version_example_model_prep.example_1', 'example_source_schema.table_3', 'example_source_schema.table_1', 'example_source_schema.table_2'])
  
  def test_dynamic_env_var_is_affecting_rendered_queries(self):
    output = dynamic_env.models['new_version_example_model'].rendered_model['new_version_example_model_prep.example_1']['rendered_query']
    rendered_query = "\nselect *, date_trunc('month', CONVERT_TIMEZONE ('UTC', 'America/New_York', getdate()))::date\nfrom  example_source_schema_public.table_1 table_1\njoin  example_source_schema_public.table_2 table_2\non table_1.id = table_2.id\njoin  example_source_schema_public.table_3 table_3\non table_2.table_3_id = table_3.id"
    self.assertEqual(output, rendered_query)
  
  def test_diff_exraction(self):
    diff = full_dynamic_env.extract_version_diff('test', all_models.api_data['models'], de_test_diff_models.api_data['models'])
    expected_output = ['test_custom_prep_schema.enrich_example_1']
    self.assertEqual(expected_output, diff)
  
  def test_diff_lineage(self):
    expected_output = ['test_custom_prep_schema.enrich_example_1', 'test_model_2.example_1']
    self.assertEqual(expected_output, full_dynamic_env.diff_lineage)

  def test_dynamic_env_is_set_only_affected_tables(self):
    rendered_query = full_dynamic_env.version.api_data['models']['test_model_2']['rendered_model']['test_model_2.example_1']['rendered_query']
    expected_output = '\nselect *\nfrom  example_model.example_3\njoin  test_custom_prep_schema.enrich_example_1\njoin  example_model_prep.example_1'
    self.assertEqual(expected_output, rendered_query)
  #add test case for version without sql diff
if __name__ == '__main__':
  unittest.main()
