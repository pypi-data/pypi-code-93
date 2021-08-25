# run pip install -r requirements.txt
from sqlpie.compiler import Compiler
from sqlpie.project import Project
import glob
import sys
import yaml
import dag
from os import listdir
from os.path import isfile, join
from sqlpie.exceptions import UnknownSourceError, FailedAddingEdge


class ModelEngine:

  def __init__(self, model, vars_payload={}):
    self.dynamic_env = None
    self.dynamic_env_diff = None
    self._vars_payload = vars_payload
    self.model_config = Project.get_model_config(model)
    self.model_path = self._get_model_path(model)
    self._model_queries_path = glob.glob(self.model_path)
    self.sources_conf = Project.sources()
    if 'dynamic_env' in vars_payload.keys():
      self.dynamic_env = vars_payload['dynamic_env']
      self.project_models = Project.models(self.dynamic_env)
      self.all_models = self.project_models['models']
      self.all_prep_models = self.project_models['prep_models']
      self.dynamic_env_prod_index = self.project_models['dynamic_env_prod_index']
      self.dynamic_env_model = Project.dynamic_env_model(self.dynamic_env, model)
      self.dynamic_env_prep_model = self._set_prep_model_name(self.dynamic_env)
      if 'dynamic_env_diff' in self._vars_payload.keys():
        self.dynamic_env_diff = self._vars_payload['dynamic_env_diff']
    else:
      self.project_models = Project.models()
      self.all_models = self.project_models['models']
      self.all_prep_models = self.project_models['prep_models']
    self.model = model
    self.prep_model = self._set_prep_model_name()
    self._set_payload()
    self.model_sources = {}
    self._current_query = None
    self.rendered_model = {}
    self.edges = []
    self.dag = dag.DAG()
    self._render_model()
  
  def _get_model_path(self, model):
    return f"./models/{model}/*.sql"
  
  def _load_snippets(self):
    path = './snippets'
    sys.path.append(path)
    snippets = [f for f in listdir(path) if isfile(join(path, f))]
    payload = {}
    for snippet in snippets:
      prefix = snippet.split('.')[0]
      suffix = snippet.split('.')[1]
      if suffix == 'py' and prefix != '__init__':
        modname = prefix
        mod = __import__(modname)
        payload[modname] = mod
    return payload
  
  #invoked when the source block is rendered
  def source(self, source_name, table_name):
    source_table = f"{source_name}.{table_name}"
    source_type = None
    if source_name in list(Project.sources().keys()):
      source_schema = self.sources_conf[source_name]['schema_name']
      source_type = 'source'
    if self.dynamic_env:
      if self.dynamic_env_diff:
        if source_table in self.dynamic_env_diff:
          model = self.dynamic_env_model
          prep_model = self.dynamic_env_prep_model
        elif source_type is None:
          source_table = f"{self.dynamic_env_prod_index[source_name]}.{table_name}"
          model = self.model
          prep_model = self.prep_model
          source_type = 'dynamic_env_prod_pointer'
          source_schema = model
      else:
        model = self.dynamic_env_model
        prep_model = self.dynamic_env_prep_model
    else:
      model = self.model
      prep_model = self.prep_model
    if source_type is None:
      if source_name == model:
        source_name = model
        source_schema = source_name
        source_type = 'model'
      elif source_name ==  prep_model:
        source_name = model
        source_schema = source_name
        source_type = 'prep_model'
      elif source_name in self.all_models:
        source_schema = source_name
        source_type = 'other_model'
      elif source_name in self.all_prep_models:
        source_schema = source_name
        source_type = 'other_prep_model'
      else:
        raise UnknownSourceError(UnknownSourceError.message(source_table))
      update_method = None
    destination_table =f"{self._execution_metadata['destination_schema']}.{self._execution_metadata['destination_table']}"
    self.model_sources[source_table] = { 
                                          'source_type': source_type,
                                          'source_name': source_name, 
                                          'schema': source_schema,
                                          'table_name': source_table,
                                          'table_short_name': table_name,
                                          'destination_table': destination_table
                                        }
    self.dag.add_node_if_not_exists(destination_table)
    self.dag.add_node_if_not_exists(source_table)
    edge = [source_table, destination_table]
    if edge not in self.edges:
      self.edges.append(edge)
      try:
        self.dag.add_edge( source_table, destination_table)
      except dag.DAGValidationError:
        raise FailedAddingEdge(FailedAddingEdge.message(source_table, destination_table))
    if source_name in self.sources_conf.keys():
      return f"{self.sources_conf[source_name]['schema_name']}.{table_name}"
    else:
      return source_table

  #invoked when the config block is rendered
  def query_execution_config(self, **kargs):
    #input validation 
    if self.dynamic_env:
      model = self.dynamic_env_model
      prep_model = self.dynamic_env_prep_model
    else:
      model = self.model
      prep_model = self.prep_model

    self._execution_metadata = kargs
    if 'prep' in self._execution_metadata.keys():
      if self._execution_metadata['prep'] == True:
        self._execution_metadata['destination_schema'] = prep_model
    else:
      self._execution_metadata['destination_schema'] = model
    return ''

  def _update_current_query(self, query):
    self.current_query = query
  
  def _parse_template_query(self, template):
    config = '\n' + template.split('}}')[0] + "}}"
    query = str('}}').join( template.split('}}')[1:])
    return {'config': config, 'query': query}

  def _render_model(self):
    for path in self._model_queries_path:
      self._update_current_query(path)
      rendered_query =  self._render_query(path)
      file_suffix = path.split('/')[-1].split('.')[1]
      if file_suffix == 'sql':
        table_short_name = self._execution_metadata['destination_table']
        table_name = f"{self._execution_metadata['destination_schema']}.{table_short_name}"
        self.rendered_model[table_name] = {}
        self.rendered_model[table_name]['rendered_query'] = rendered_query
        query_template = open(path, 'r')
        self.rendered_model[table_name]['template'] = self._parse_template_query(query_template.read())
        query_template.close()
        self.rendered_model[table_name]['execution_metadata'] = self._execution_metadata
        self.rendered_model[table_name]['table_short_name'] = table_short_name
        self.rendered_model[table_name]['file_path'] = path
        if 'description' in self.model_config.keys():
          if table_short_name in self.model_config['description']['tables'].keys():
            self.rendered_model[table_name]['description'] = self.model_config['description']['tables'][table_short_name]


  def _render_query(self, path=None):
    rendered_query = Compiler(path, self.payload).query_string[1:]
    return rendered_query
  
  def _set_source_conf(self):
    sources_config_file = open("./config/sources.yml", "r")
    self.sources_conf = yaml.load(sources_config_file, Loader=yaml.FullLoader)
    sources_config_file.close()

  def _set_prep_model_name(self, dynamic_env = None):
    if dynamic_env:
      if self.model_config and 'prep_schema' in self.model_config.keys():
        return f"{dynamic_env}_{self.model_config['prep_schema']}"
      else:
        return f"{self.dynamic_env_model}_prep"
    else:
      if self.model_config and 'prep_schema' in self.model_config.keys():
        return self.model_config['prep_schema']
      else:
        return f"{self.model}_prep"
    
  def _set_payload(self):
    self.payload = self._load_snippets()
    self.payload['vars'] = self._vars_payload
    self.payload['config'] = self.query_execution_config
    self.payload['source'] = self.source
    project_payload = Project.project_payload()
    if self.dynamic_env:
      self.payload['model'] = self.dynamic_env_model
      self.payload['prep_model'] = self.dynamic_env_prep_model
      if self.dynamic_env_diff:
        project_payload_dynamic_env = Project.project_payload(dynamic_env=self.dynamic_env, dynamic_env_diff=self.dynamic_env_diff)
      else:
        project_payload_dynamic_env = Project.project_payload(dynamic_env=self.dynamic_env)
      for i in range(len(project_payload)):
        self.payload[project_payload[i]] = project_payload_dynamic_env[i]
    else:
      self.payload['model'] = self.model
      self.payload['prep_model'] = self.prep_model
     
      for source_or_model in project_payload:
        self.payload[source_or_model] = source_or_model

  def print_query(self, destination_table):
    print(self.rendered_model[destination_table])
    return self.rendered_model[destination_table]
