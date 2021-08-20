import os
from hashlib import md5
from collections.abc import Iterable
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient

def assert_mlflow_tracking_uri(mlflow_tracking_uri = None):
  assert mlflow_tracking_uri or 'MLFLOW_TRACKING_URI' in os.environ,\
  "Specify mlflow_tracking_uri or the MLFLOW_TRACKING_URI environment variable."
  mlflow_tracking_uri = os.environ['MLFLOW_TRACKING_URI'] if not mlflow_tracking_uri else mlflow_tracking_uri
  return mlflow_tracking_uri

def assert_mlflow_experiment_name(mlflow_experiment_name = None):
  assert mlflow_experiment_name or 'MLFLOW_EXPERIMENT_NAME' in os.environ,\
    "Specify mlflow_experiment_name or the MLFLOW_EXPERIMENT_NAME environment variable."
  mlflow_experiment_name = os.environ['MLFLOW_EXPERIMENT_NAME'] if not mlflow_experiment_name else mlflow_experiment_name
  return mlflow_experiment_name

def assert_mlflow_experiment_id(mlflow_experiment_id = None):
  assert mlflow_experiment_id or 'MLFLOW_EXPERIMENT_ID' in os.environ,\
    "Specify mlflow_experiment_id or the MLFLOW_EXPERIMENT_ID environment variable."
  mlflow_experiment_id = os.environ['MLFLOW_EXPERIMENT_ID'] if not mlflow_experiment_id else mlflow_experiment_id
  return mlflow_experiment_id

def get_client(mlflow_tracking_uri = None):
  mlflow_tracking_uri = assert_mlflow_tracking_uri()
  return MlflowClient(mlflow_tracking_uri)  

def terminate_parent_run(client = None, parent_run = None):
  client = client if client else get_client()
  parent_run = parent_run if parent_run else get_parent_run(client)
  if parent_run:
    client.set_terminated(parent_run.info.run_id)

def get_parent_run(client, experiment_name = None, experiment_id = None):
  if not experiment_id:
    experiment_name = assert_mlflow_experiment_name(experiment_name)
    experiment = client.get_experiment_by_name(experiment_name)
    experiment_id = experiment.experiment_id
  else:
    experiment_id = assert_mlflow_experiment_id(experiment_id)
    experiment = client.get_experiment(experiment_id)
    experiment_name = experiment.name

  query = f"""attribute.status='RUNNING'
    AND tags.mlflow.runName='{experiment_name}'
  """
  runs = client.search_runs(experiment_ids = experiment_id, 
                            filter_string = query,
                            run_view_type=ViewType.ACTIVE_ONLY)
  
  if runs and len(runs) == 1:
    parent_run = runs[0]
    if 'tags.mlflow.parentRunId' in parent_run.data.tags:
      return None
    else:
      return parent_run
  else:
    return None

def get_existing_run(mlflow_tracking_uri = None, mlflow_experiment_name = None, client = None, run = None):
    client = get_client(mlflow_tracking_uri) if not client else client
    return client.get_run(run.info.run_id)
    
def get_active_child_run(mlflow_tracking_uri = None, mlflow_experiment_name = None, client = None, parent_run = None):
    client = get_client(mlflow_tracking_uri) if not client else client
    parent_run = get_parent_run(client, experiment_name = mlflow_experiment_name) if not parent_run else parent_run
    if parent_run and 'RUNNING' == parent_run.info.status:
        experiment_id = parent_run.info.experiment_id
        parent_run_id = parent_run.info.run_id
        runs = client.search_runs(experiment_ids=experiment_id, 
                                  filter_string = f"""
                                  tags.mlflow.parentRunExperimentId='{experiment_id}'
                                  AND tags.mlflow.parentRunId='{parent_run_id}'
                                  AND attribute.status='RUNNING'
                                  """,
                                  run_view_type=ViewType.ACTIVE_ONLY)  
        if runs and len(runs) == 1:
            return runs[0]
        else:
            return None
    else:
        return None

def make_feature_set_ids(feature_set_dict = None, hparams_dict = None):
  result = dict()
  for feature_set_key, feature_set_names in (feature_set_dict.items() if feature_set_dict else dict().items()):
    feature_set_names = [feature_set_names] if isinstance(feature_set_names, str) else feature_set_names
    if isinstance(feature_set_names, Iterable):
      src = []
      for hparam in feature_set_names:
        if hparam in hparams_dict:
          src.append(f"{hparam}={hparams_dict[hparam]}\n")
        else:
          raise KeyError(hparam)
      val = ("".join(src))[:-1]
    else:
      raise KeyError(feature_set_key)          

    result.update( { feature_set_key : md5(str.encode( val )).hexdigest() } )

  return result

def get_active_run_hp_set_id(mlflow_tracking_uri = None, mlflow_experiment_name = None, hp_set_id = None):
  return get_active_run_feature_set_id(mlflow_tracking_uri, mlflow_experiment_name, hp_set_id)

def get_active_run_feature_set_id(mlflow_tracking_uri = None, mlflow_experiment_name = None, feature_set_id = None):
  active_run = get_active_child_run(mlflow_tracking_uri, mlflow_experiment_name)
  if active_run is not None:
    assert feature_set_id \
            and isinstance(feature_set_id, str) \
            and feature_set_id in active_run.data.tags, \
            f"The feature_set_id {feature_set_id} be an existing tag in the run {active_run.info.run_id}"

    return active_run.data.tags[feature_set_id]

def get_active_run_params(mlflow_tracking_uri = None, mlflow_experiment_name = None, client = None, parent_run = None, output = 'bash'):
  output_options = ['bash', 'json']
  assert output and type(output) is str and output in output_options, f"The output must one of the following string values: {output_options}"

  client = get_client(mlflow_tracking_uri) if not client else client
  # parent_run = get_parent_run(client, experiment_name = mlflow_experiment_name) if not parent_run else parent_run

  while get_parent_run(client) is not None:
    active_run = get_active_child_run(mlflow_tracking_uri, mlflow_experiment_name)
    if active_run is not None:
        if 'bash' == output:
          return "\n".join([f"{k}='{v}'" for k, v in active_run.data.params.items()])
        elif 'json' == output:
          return active_run.data.params
        else:
          raise RuntimeError(f"Unsupported output type {output}")