import pandas as pd
import os
import glob
from pathlib import Path
import json

from mlsriracha.interfaces.process import ProcessInterface
from mlsriracha.plugins.kubernetes.common.helper import s3_download, s3_upload, azblob_download


class KubernetesProcess(ProcessInterface):

    def __init__(self):
        print('Selected Kubernetes profile')
        
        Path('/opt/ml/processing/input/data').mkdir(parents=True, exist_ok=True)
        Path('/opt/ml/processing/output/data').mkdir(parents=True, exist_ok=True)

        channel_var = 'input_' + channel
        if channel_var in self.get_env_vars():

            print(f'Found channel request: {channel_var}' )
            # create local path to save this
            # if S3
        
            if 's3' in self.get_env_vars()[channel_var]:
                
                s3_download(self.get_env_vars()[channel_var], f'/opt/ml/processing/input/data/{channel}/')
                

            # if Azure
            if 'blob.core.windows' in self.get_env_vars()[channel_var]:

                azblob_download(self.get_env_vars()[channel_var], f'/opt/ml/processing/input/data/{channel}/')

    def get_env_vars(self):
        envs = {}
        for k, v in os.environ.items():
            if k.startswith('sriracha_'):
                try: 
                    value = float(v)   # Type-casting the string to `float`.
                    if value.is_integer():
                        value = int(value)
                except ValueError:
                    value = v
                envs[k.replace('sriracha_', '')] = value
        return envs

    def input_as_dataframe(self, filename):
        """
        The function returns a panda dataframe for the input channel artifacts.

        AWS SageMaker passes all values in FileMode from the S3 bucket into the 
        input processing data "channels" when starting your container.
        This function takes in the channel and merges all CSV files per channel
        into a dataframe for reading.

        Arguments:
            channel (str): The name of the channel which contains the given filename
        """
        if filename: 
            csv_files = glob.glob(os.path.join(f'/opt/ml/processing/inputs/{filename}'))
        else:    
            csv_files = glob.glob(os.path.join(f'/opt/ml/processing/inputs/*.csv'))
        print(f'Files in input directory: {csv_files}')
        # loop over the list of csv files
        fileBytes = []
        for f in csv_files:
    
            # read the csv file
            df = pd.read_csv(f)
            fileBytes.append(df)
        frame = pd.concat(fileBytes, axis=0, ignore_index=True)     
        return frame 
  
    
    def log_artifact(self, filename=''):
        """
        The path to the output artifacts.

        Your algorithm should write all final model artifacts to this directory.
        Amazon SageMaker copies this data as a single object in compressed tar
        format to the S3 location that you specified in the CreateTrainingJob
        request. If multiple containers in a single training job write to this
        directory they should ensure no file/directory names clash. Amazon SageMaker
        aggregates the result in a tar file and uploads to S3.

        Arguments:
            filename (str): The name of the file which will be written back to S3

        Returns:
            path (str): The absolute path to the model output directory
        """
        return os.path.join(os.sep, 'opt', 'ml', 'processing', 'outputs', filename)

    def finish(self):
        if 'output' in self.get_env_vars():
            upload_uri = self.get_env_vars()['output']
            print(f'Found output: {upload_uri}' )
            # create local path to save this
            
            if 's3' in upload_uri:
                s3_upload(upload_uri, f'/opt/ml/output/')

            # if Azure
            elif 'blob.core.windows' in upload_uri:
                return
                # azblob_download(upload_uri, f'/opt/ml/output/')