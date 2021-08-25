import requests
import pickle
from io import BytesIO
import pandas as pd
import torch
from os.path import exists
import os


class ModelWeightDataset:
    def __init__(self, filename, num_spaces_searched):
        self.file_name = filename
        self.num_spaces_searched = num_spaces_searched
        self.baseline_url = None
        self.optimizer_results = None
        self.ray_tune_dfs = None
        self._wandb_dataframe = None

    @property
    def wandb_dataframe(self):
        if self._wandb_dataframe is None:
            self._wandb_dataframe = pd.read_csv(self.file_name)
        return self._wandb_dataframe

    @property
    def optimizer_result(self, num=None):
        # check if baseline url is None
        if not self.baseline_url:
            raise AttributeError(
                "Baseline url has not been set. Cannot access google cloud storage without base url."
            )
        if not self.optimizer_results:
            if not num:
                # return all
                return self.optimizer_results
            else:
                return self.optimizer_results[num]
        else:
            self.optimizer_results = []
            # get each byte stream of optimizer results from google cloud storage
            for i in range(self.num_spaces_searched):
                optimizer_bytes = requests.get(
                    self.baseline_url + "/optimizer_result{}.pkl".format(i)
                ).content
                optimizer = pickle.loads(optimizer_bytes)
                self.optimizer_results.append(optimizer)
            if not num:
                # return all
                return self.optimizer_results
            else:
                return self.optimizer_results[num]

    @property
    def ray_tune_dataframes(self, num=None):
        # check if baseline url is None
        if not self.baseline_url:
            raise AttributeError(
                "Baseline url has not been set. Cannot access google cloud storage without base url."
            )
        if not self.ray_tune_dfs:
            if not num:
                # return all
                return self.ray_tune_dfs
            else:
                return self.ray_tune_dfs[num]
        else:
            self.ray_tune_dfs = []
            # get the csvs
            for i in range(self.num_spaces_searched):
                df_bytes = requests.get(
                    self.baseline_url + "/space{}.csv".format(i)
                ).content
                df = pd.read_csv(BytesIO(df_bytes))
                self.ray_tune_dfs.append(df)
            if not num:
                # return all
                return self.ray_tune_dfs
            else:
                return self.ray_tune_dfs[num]

    def get_pytorch_weights(self, experiment_name, trial_name):
        """Return state dict of specific trial's pytorch model"""
        if not self.baseline_url:
            raise AttributeError(
                "Baseline url has not been set. Cannot access google cloud storage without base url."
            )
        weights_file_name = "/tmp/{}_{}.pt_model.pt".format(experiment_name, trial_name)
        # get the weights either from cache or google cloud
        if exists(weights_file_name):
            pass
        else:
            weights = requests.get(
                self.baseline_url + "/model_weights/{}.pt_model.pt".format(trial_name)
            ).content
            with open(weights_file_name, "wb") as f:
                f.write(weights)
        weights = torch.load(weights_file_name)
        # return the weights
        return weights

    def get_tensorflow_weights(self, experiment_name, trial_name):
        """Get the model weights/definitions from the google cloud storage, save to folder"""
        weights_file_name = "/tmp/{}_{}tf_model/".format(experiment_name, trial_name)
        if exists(weights_file_name):
            pass
        else:
            os.mkdir(weights_file_name)
            os.mkdir(weights_file_name + "/variables")
            # get each kind of file needed
            with open(weights_file_name + "/saved_model.pb", "wb") as f:
                saved_model = requests.get(
                    self.baseline_url
                    + "/model_weights/{}tf_model/saved_model.pb".format(trial_name)
                ).content
                f.write(saved_model)
            with open(
                weights_file_name + "/variables/variables.data-00000-of-00001", "wb"
            ) as f:
                variables_data = requests.get(
                    self.baseline_url
                    + "/model_weights/{}tf_model/variables/variables.data-00000-of-00001".format(
                        trial_name
                    )
                ).content
                f.write(variables_data)
            with open(weights_file_name + "/variables/variables.index", "wb") as f:
                variables_index = requests.get(
                    self.baseline_url
                    + "/model_weights/{}tf_model/variables/variables.index".format(
                        trial_name
                    )
                ).content
                f.write(variables_index)
        print(
            "Tensorflow Model definition has been saved to {}. Feel free to call get_tensorflow_model(trial_name).".format(
                weights_file_name
            )
        )
        return

    def get_pytorch_model(self, trial_name):
        raise NotImplementedError

    def get_tensorflow_model(self, trial_name):
        raise NotImplementedError


# class TrialResult:
#     def __init__(self, name):
#         self.name = name
#         self.url = name

# @property
# def pytorch_weights(self):
#     if not hasattr(self, "pytorch_weights"):
#         # load the pt model from google cloud storage
#
