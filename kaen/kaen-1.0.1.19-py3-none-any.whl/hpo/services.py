import os
import time

import optuna
from optuna.samplers import TPESampler
from optuna.trial import TrialState

import argparse

import mlflow
from mlflow import ActiveRun
from mlflow.entities import RunStatus
from mlflow.tracking import MlflowClient

import numpy as np

from laai.hpo.mlflow_utils import get_parent_run, get_active_child_run, make_feature_set_ids, get_client, get_existing_run

class BaseMLFlowService():
  def __init__(self):
    pass

  @property
  def seed(self):
    return self._seed

  @seed.setter
  def seed(self, seed):
    self._seed = seed

  @property
  def mlflow_client(self):
    return self._mlflow_client

  @mlflow_client.setter
  def mlflow_client(self, mlflow_client):
    self._mlflow_client = mlflow_client

  @property
  def num_trials(self):
    return self._num_trials

  @num_trials.setter
  def num_trials(self, num_trials):
    self._num_trials = num_trials

  @property
  def job_start_delay_sec(self):
    return self._job_start_delay_sec

  @job_start_delay_sec.setter
  def job_start_delay_sec(self, job_start_delay_sec):
    self._job_start_delay_sec = job_start_delay_sec

  @property
  def run_update_delay_sec(self):
    return self._run_update_delay_sec

  @run_update_delay_sec.setter
  def run_update_delay_sec(self, run_update_delay_sec):
    self._run_update_delay_sec = run_update_delay_sec    

  @property
  def mlflow_experiment_name(self):
    return self._mlflow_experiment_name

  @mlflow_experiment_name.setter
  def mlflow_experiment_name(self, mlflow_experiment_name):
    self._mlflow_experiment_name = mlflow_experiment_name

  @property
  def mlflow_experiment_id(self):
    return self._mlflow_experiment_id

  @mlflow_experiment_id.setter
  def mlflow_experiment_id(self, mlflow_experiment_id):
    self._mlflow_experiment_id = mlflow_experiment_id

  @property
  def get_mlflow_tracking_uri(self):
    return self._mlflow_tracking_uri

  @get_mlflow_tracking_uri.setter
  def get_mlflow_tracking_uri(self, get_mlflow_tracking_uri):
    self._get_mlflow_tracking_uri = get_mlflow_tracking_uri

  def on_experiment_start(self, experiment, parent_run):
    pass

  def on_experiment_end(self, experiment, parent_run):
    pass

  def on_run_create(self, run):
    pass

  def on_run_start(self, run):
    pass

  def on_run_update(self, run, idx):
    pass

  def on_run_end(self, run):
    pass

  def hparams(self):
    return {
      'seed': np.random.randint(low = 0, high = np.iinfo(np.int32).max - 1)
    }

  def hparams_set_id(self):
    return dict()

  def run(self, 
          num_trials = 1, 
          mlflow_tracking_uri = None, 
          mlflow_experiment_name = None,
          hpo_seed = None, 
          job_start_delay_sec = 1, 
          run_update_delay_sec = 0):

    assert num_trials and isinstance(num_trials, int) and num_trials > 0, "The value of num_trials must be a positive integer."
    self.num_trials = num_trials

    assert isinstance(job_start_delay_sec, int) and (job_start_delay_sec > -1), "The value of job_start_delay_sec should be zero or a positive integer"
    self.job_start_delay_sec = job_start_delay_sec

    assert isinstance(run_update_delay_sec, int) and run_update_delay_sec > -1, "The value of run_update_delay_sec should be zero or a positive integer"
    self.run_update_delay_sec = run_update_delay_sec

    #set the pseudorandom number seed
    if not hpo_seed:
      from datetime import datetime
      hpo_seed = int(datetime.now().microsecond)
      print('WARNING: pseudorandom number generator seed value is missing, initializing the seed based on the current timestamp.')
    self.seed = hpo_seed
    np.random.seed(self.seed)
    
    #ensure that the mlflow tracking uri is set correctly
    if not mlflow_tracking_uri:
      assert 'MLFLOW_TRACKING_URI' in os.environ, "Specify mlflow_tracking_uri or the MLFLOW_TRACKING_URI environment variable."      
      mlflow_tracking_uri = os.environ['MLFLOW_TRACKING_URI']
    self.mlflow_tracking_uri = mlflow_tracking_uri

    #create an mlflow client
    self.mlflow_client = get_client(self.mlflow_tracking_uri)

    #ensure that the mlflow_experiment_name is set correctly
    if not mlflow_experiment_name:
      assert 'MLFLOW_EXPERIMENT_NAME' in os.environ, "Specify mlflow_experiment_name or the MLFLOW_EXPERIMENT_NAME environment variable."  
      mlflow_experiment_name = os.environ['MLFLOW_EXPERIMENT_NAME']
    self.mlflow_experiment_name = mlflow_experiment_name

    #create an mlflow experiment unless exists
    experiment = self.mlflow_client.get_experiment_by_name(self.mlflow_experiment_name)
    if not experiment or experiment.lifecycle_stage is not 'active':
      self.mlflow_experiment_id = self.mlflow_client.create_experiment(self.mlflow_experiment_name)
      experiment = self.mlflow_client.get_experiment_by_name(self.mlflow_experiment_name)
    else:
      self.mlflow_experiment_id = experiment.experiment_id
    
    #create a parent run in the experiment
    mlflow.start_run(run_name = self.mlflow_experiment_name,
                    experiment_id = self.mlflow_experiment_id)  
                      
    parent_run = mlflow.active_run()

    for k, v in {"hpo_seed": self.seed,
                 "num_trials": self.num_trials,
                "job_start_delay_sec": self.job_start_delay_sec,
                "run_update_delay_sec": self.run_update_delay_sec,}.items():
      self.mlflow_client.set_tag(parent_run.info.run_id, k, v)

    parent_run_id = parent_run.info.run_id
  
    self.on_experiment_start(experiment, parent_run)
    try:
      while parent_run and self.num_trials > 0:
        self.num_trials -= 1

        #wait to start a new child run
        time.sleep(self.job_start_delay_sec)

        #create a child run    
        parent_run = get_parent_run(self.mlflow_client,
                          self.mlflow_experiment_name,
                          self.mlflow_experiment_id)

        #CREATE A RUN IN A STATE (UNFINISHED)
        run = self.mlflow_client.create_run(experiment.experiment_id, 
          tags = {"mlflow.parentRunId": parent_run.info.run_id})

        print(f"Created a run {run.info.run_id}({run.info.status})")
        self.on_run_create(run)

        #log the hyperparameters in the mlflow run
        self.__hparams = self.hparams()
        for k, v in (self.__hparams if self.__hparams else {}).items():
          self.mlflow_client.log_param(run.info.run_id, k, v)

        #log the tags for the feature sets
        feature_set_ids = make_feature_set_ids(self.hparams_set_id(), self.__hparams)
        for k, v in (feature_set_ids if feature_set_ids else {}).items():
          self.mlflow_client.set_tag(run.info.run_id, k, v)

        with ActiveRun(parent_run):  
          try:

            #UPDATE THE RUN TO (RUNNING) STATE
            run = mlflow.start_run(experiment_id = experiment.experiment_id, 
                                run_id = run.info.run_id,
                                nested = True)
            self.mlflow_client.set_tag(run.info.run_id, "mlflow.parentRunExperimentId", experiment.experiment_id)
            self.on_run_start(run)

            idx = 0
            while run \
              and 'RUNNING' == run.info.status \
              and parent_run \
              and 'RUNNING' == parent_run.info.status:

              time.sleep(self.run_update_delay_sec)

              for k, v in (run.data.metrics if run.data.metrics else {}).items():
                print(f"{run.info.run_id} {k}={v}")
            
              run = self.mlflow_client.get_run(run.info.run_id)
              parent_run = get_parent_run(self.mlflow_client,
                                self.mlflow_experiment_name,
                                self.mlflow_experiment_id)     
              self.on_run_update(run, idx)

              idx += 1             
              print(f"Waiting on job {run.info.run_id}({run.info.status})")

          finally:
            self.on_run_end(run)

    finally:
      self.on_experiment_end(experiment, parent_run)

      if parent_run:
        self.mlflow_client.set_terminated(parent_run.info.run_id) 
        print(f"Terminated parent run: {parent_run.info.run_id}({run.info.status})")    
      else:
        print(f"Terminated parent run: {parent_run_id}")

class BaseOptunaService(BaseMLFlowService):
  def on_experiment_start(self, experiment, parent_run):
    seed = super().seed
    experiment_name = super().mlflow_experiment_name    

    #create the hyperparameter study
    self._study = optuna.create_study( study_name = experiment_name,
      pruner = optuna.pruners.SuccessiveHalvingPruner(),
      sampler = TPESampler( seed = seed) )

  def on_run_create(self, run):
    self._trial = self._study.ask()
    super().mlflow_client.set_tag(run.info.run_id,
      "optuna.trial_number", self._trial.number)

  def on_run_update(self, run, idx):
    trial = self._trial

    loss = run.data.metrics['loss'] if 'loss' in run.data.metrics else None
    step = run.data.metrics['step'] if 'step' in run.data.metrics else None

    if loss and step:
      trial.report(loss, step)
      if trial.should_prune():
          print(f"{run.info.run_id}: pruning...")        
          super().mlflow_client.set_terminated(run.info.run_id, status = 'KILLED')

  def on_run_end(self, run):
    if 'loss' in run.data.metrics:
      self._study.tell(self._trial, run.data.metrics['loss'])
    else:
      self._study.tell(self._trial, None, state = TrialState.FAIL)


class XorExperimentService(BaseOptunaService):
  def hparams(self):
    trial = self._trial

    #define hyperparameters
    return {
      "seed": trial.suggest_int('seed', 0, np.iinfo(np.int32).max - 1),
        
      "bins": trial.suggest_categorical('bins', [32, 48, 64, 96, 128]),
        
      "optimizer": trial.suggest_categorical('optimizer', ['SGD', 'Adam']),
        
      "lr": trial.suggest_loguniform('lr', 89e-3, 91e-3),
        
      "num_hidden_neurons": [trial.suggest_int(f"num_hidden_layer_{layer}_neurons", 5, 17) \
                                for layer in range(trial.suggest_int('num_layers', 1, 2))],
      
      "batch_size": trial.suggest_categorical('batch_size', [32, 64, 128]),
        
      "max_epochs": trial.suggest_int('max_epochs', 100, 400, log = True)
    }

  def hparams_set_id(self):
    #specify the subsets of hyperparameter name/values to id
    return {
        "hp_bin_id": 'bins'
    }    

  def on_experiment_end(self, experiment, parent_run):
    study = self._study
    try:
      for key, fig in {
        "plot_param_importances": optuna.visualization.plot_param_importances(study),
        "plot_parallel_coordinate": optuna.visualization.plot_parallel_coordinate(study, params=["max_epochs", "num_hidden_layer_0_neurons"]),
        "plot_parallel_coordinate_max_epochs_lr": optuna.visualization.plot_parallel_coordinate(study, params=["max_epochs", "lr"]),
        "plot_parallel_coordinate_lr_layer_0": optuna.visualization.plot_parallel_coordinate(study, params=["lr", "num_hidden_layer_0_neurons"]),
        "plot_contour": optuna.visualization.plot_contour(study, params=["max_epochs", "num_hidden_layer_0_neurons"]),
        "plot_contour_max_epochs_lr": optuna.visualization.plot_contour(study, params=["max_epochs", "lr"]),
      }.items():
        fig.write_image(key + ".png")
        self.mlflow_client.log_artifact(run_id = parent_run.info.run_id, 
                            local_path = key + ".png")
    except:
      print(f"Failed to correctly persist experiment visualization artifacts")
              
    #log the dataframe with the study summary  
    study.trials_dataframe().describe().to_html(experiment.name + ".html")  
    self.mlflow_client.log_artifact(run_id = parent_run.info.run_id, 
                        local_path = experiment.name + ".html")
          
    #log the best hyperparameters in the parent run
    self.mlflow_client.log_metric(parent_run.info.run_id, "loss", study.best_value)
    for k, v in study.best_params.items():
      self.mlflow_client.log_param(parent_run.info.run_id, k, v)

    print('Best trial: {} value: {} params: {}\n'.format(study.best_trial, study.best_value, study.best_params))    