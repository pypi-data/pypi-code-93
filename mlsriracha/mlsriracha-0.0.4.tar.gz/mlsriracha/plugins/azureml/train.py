import os
import pandas as pd
from pathlib import Path

from mlsriracha.interfaces.train import TrainInterface

class AzureMlTrain(TrainInterface):

    def __init__(self):
        print('Using Azure ML Sriracha profile')
        Path('./outputs/model').mkdir(parents=True, exist_ok=True)

    def get_hyperparameters(self):
        envs = {}
        for k, v in os.environ.items():
            if k.startswith('sriracha_hp_'):
                try: 
                    # Azure requires all env to be strings, so return as num if parseable
                    value = float(v)   # Type-casting the string to `float`.
                    if value.is_integer():
                        value = int(value)
                except ValueError:
                    value = v

                envs[k.replace('sriracha_hp_', '')] = value
        return envs


    def get_env_vars(self):
        envs = {}
        for k, v in os.environ.items():
            if k.startswith('sriracha_'):
                try: 
                    # Azure requires all env to be strings, so return as num if parseable
                    value = float(v)   # Type-casting the string to `float`.
                    if value.is_integer():
                        value = int(value)
                except ValueError:
                    value = v

                envs[k.replace('sriracha_', '')] = value
        return envs

    def input_as_dataframe(self, channel='training'):
        """
        The path to input artifacts.

        In Azure, mlctl passes environment variables that map to the 
        train.yaml inputs that the user defines.

        Arguments:
            channel (str): The name of the channel which contains the given filename
            filename (str): The name of the file within a specific channel

        Returns:
            path (str): The absolute path to the specified channel file
        """

        # channel --> environmental variable names
        data_directories = {
            'training': "AZURE_ML_INPUT_training",
            'validation': "AZURE_ML_INPUT_validation",
            'testing': "AZURE_ML_INPUT_testing"
        }

        if channel in data_directories.keys():
            azure_mount_file = os.environ.get(data_directories[channel])
            print(f'azure_mount_file={azure_mount_file}')
            data = pd.read_csv(azure_mount_file)
            return data

        else:
            print('Incorrect data channel type. Options are training, validation, and testing.')
            return null
    
    def log_artifact(self, filename=''):
        """
        The path to the output artifacts.

        Your algorithm should write all final model artifacts to this directory.
        Azure ML copies this data as a folder into the console as a Run output.

        Arguments:
            filename (str): The name of the file which will be written back to S3

        Returns:
            path (str): The absolute path to the model output directory
        """
        cwd = os.getcwd()
        return os.path.join(cwd, 'outputs', 'model', filename)

    def finish(self):
        return True