import os
import argparse
import json 

import time
from datetime import datetime

import numpy as np
import torch as pt
import pandas as pd
import pytorch_lightning as pl

from torch.nn.functional import mse_loss

from mlflow.entities import RunStatus
from laai.hpo.mlflow_utils import get_client, get_parent_run, get_active_child_run, assert_mlflow_tracking_uri, assert_mlflow_experiment_name, get_existing_run
from osds.utils import ObjectStorageDataset
from torch.utils.data import DataLoader

from laai.hpo.client import BaseMLFlowClient

import optuna
from laai.hpo.services import BaseOptunaService
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



from pytorch_lightning.callbacks import Callback
class PruneRun(Callback):
  #enable run pruning
  def on_batch_end(self, trainer, pl_module):
      if (pl_module.step % 10 == 0):
          this_run = get_existing_run(run = pl_module.run)
          if this_run and not (this_run.info.status == "RUNNING"):
              print(f"Pruning {this_run.info.run_id}({this_run.info.status}) at step {pl_module.step}")
              trainer.should_stop = True



class CircleExperimentModel(pl.LightningModule):
  @staticmethod
  def build_hidden_layers(num_hidden_neurons, activation):

    #create a list of the linear (feedforward) layers
    linear_layers = [ pt.nn.Linear(num_hidden_neurons[i], num_hidden_neurons[i+1]) for i in range(len(num_hidden_neurons) - 1) ]

    #create a list with the required number of the activation functions
    #based on the number of the hidden layers
    classes = [activation.__class__] * len(num_hidden_neurons)
    
    #create a list of the activation function instances
    activation_instances = list(map(lambda x: x(), classes))

    #zip the linear layers with the activation functions 
    hidden_layer_activation_tuples = list(zip(linear_layers, activation_instances))

    #and return as a flat list
    hidden_layers = [i for sublist in hidden_layer_activation_tuples for i in sublist]

    return hidden_layers

  def __init__(self, client, run):
    super().__init__()
    self.start_ts = time.time()
    self.step = 0

    self.client = client
    self.run = run
    self.hparams = run.data.params

    #create a list of hidden layer neurons, e.g. [2, 4, 8]
    num_hidden_neurons = json.loads(self.hparams['num_hidden_neurons'])

    #define the nn model
    self.model = pt.nn.Sequential(
        pt.nn.Linear(2, num_hidden_neurons[0]),
        pt.nn.ReLU(),
        *self.build_hidden_layers(num_hidden_neurons, pt.nn.ReLU()),
        pt.nn.Linear(num_hidden_neurons[-1], 1)
    )

  def forward(self, X):
    y_est = self.model(X)
    return y_est

  def training_step(self, batch, batch_idx):
    batch_size = int( self.run.data.params['batch_size'] ) if 'batch_size' in self.run.data.params else 128
    
    batch = batch.reshape(batch_size, 3)
    y, X = batch[:, 0], batch[:, [1, 2]]
    y_est = self.forward(X).squeeze(dim = 1)#.reshape( (y.shape[0], 1) )
    loss = mse_loss( y_est, y )

    self.client.log_metric(self.run.info.run_id, "loss", loss.item(), step=self.step)
    self.client.log_metric(self.run.info.run_id, "errors", (y_est.round() - y).to(pt.int).sum().abs().item(), step=self.step)
    self.client.log_metric(self.run.info.run_id, "step", self.step, step=self.step)    
    print(f"{self.run.info.run_id}: loss={loss.item()}, step={self.step}")

    self.step += 1
    return loss

  def configure_optimizers(self):
    hparams = self.hparams
    if hparams['optimizer'] == 'Adam':
      lr = float(hparams['lr'])
      optimizer = pt.optim.Adam(self.parameters(), lr = lr)
    else:
      lr = float(hparams['lr'])
      optimizer = pt.optim.SGD(self.parameters() ,lr = lr)

    return optimizer

class CircleExperimentService(BaseOptunaService):
  def hparams(self):
    trial = self._trial

    #define hyperparameters
    return {
      "seed": trial.suggest_int('seed', 0, np.iinfo(np.int32).max - 1),
        
      "optimizer": trial.suggest_categorical('optimizer', ['Adam']),
        
      "lr": trial.suggest_loguniform('lr', 0.061, 0.071),
        
      "num_hidden_neurons": [trial.suggest_categorical(f"num_hidden_layer_{layer}_neurons", [7, 11, 13, 23]) \
                                for layer in range(trial.suggest_categorical('num_layers', [3]))],
      
      "batch_size": trial.suggest_categorical('batch_size', [128]),
        
      "max_batches": trial.suggest_int('max_batches', 150, 250, log = True)
    }

  def on_experiment_end(self, experiment, parent_run):
    study = self._study
    try:
      for key, fig in {
        "plot_param_importances": optuna.visualization.plot_param_importances(study),
        "plot_parallel_coordinate_all": optuna.visualization.plot_parallel_coordinate(study, params=["max_batches", "lr", "num_hidden_layer_0_neurons", "num_hidden_layer_1_neurons", "num_hidden_layer_2_neurons"]),
        "plot_parallel_coordinate_l0_l1_l2": optuna.visualization.plot_parallel_coordinate(study, params=["num_hidden_layer_0_neurons", "num_hidden_layer_1_neurons", "num_hidden_layer_2_neurons"]),
        "plot_contour_max_batches_lr": optuna.visualization.plot_contour(study, params=["max_batches", "lr"]),
      }.items():
        fig.write_image(key + ".png")
        self.mlflow_client.log_artifact(run_id = parent_run.info.run_id, 
                            local_path = key + ".png")
        
    except:
      print(f"Failed to correctly persist experiment visualization artifacts")
      import traceback
      traceback.print_exc()
              
    #log the dataframe with the study summary  
    study.trials_dataframe().describe().to_html(experiment.name + ".html")  
    self.mlflow_client.log_artifact(run_id = parent_run.info.run_id, 
                        local_path = experiment.name + ".html")
          
    #log the best hyperparameters in the parent run
    self.mlflow_client.log_metric(parent_run.info.run_id, "loss", study.best_value)
    for k, v in study.best_params.items():
      self.mlflow_client.log_param(parent_run.info.run_id, k, v)

    print('Best trial: {} value: {} params: {}\n'.format(study.best_trial, study.best_value, study.best_params))    

class CircleExperiment(BaseMLFlowClient, Callback):
    def on_run_start(self, run_idx, run):
        seed = int(run.data.params['seed']) if 'seed' in run.data.params else int( datetime.now().microsecond )
        print(f"{run}({run.info.status}) using seed={seed}")
        np.random.seed(seed)
        pt.manual_seed(seed)

        batch_size = int( run.data.params['batch_size'] )
        train_dl = DataLoader(ObjectStorageDataset(f"s3://dc-taxi-74765ef3897d44692b78bb1532b85354-us-east-2/circle.csv", 
                                        storage_options = {'anon' : False },
                                        eager_load_batches = True,
                                        dtype='float32',
                                        batch_size = batch_size,))

        model = CircleExperimentModel(self.mlflow_client, run)
        max_batches = int( run.data.params['max_batches'] ) if 'max_batches' in run.data.params else 1
        trainer = pl.Trainer(limit_train_batches = max_batches,
                            max_epochs = 1, #set to 1 since the training duration is controlled by max_batches
                            callbacks = [self],
                            progress_bar_refresh_rate = 0, 
                            weights_summary = None,)

        #train the model
        trainer.fit(model, train_dl)

    #enable run pruning
    def on_batch_end(self, trainer, pl_module):
        if (pl_module.step % 10 == 0):
            this_run = get_existing_run(run = pl_module.run)
            if this_run and not (this_run.info.status == "RUNNING"):
                print(f"Pruning {this_run.info.run_id}({this_run.info.status}) at step {pl_module.step}")
                trainer.should_stop = True