import os
from pathlib import Path
from google.cloud import storage
from google.cloud.storage.blob import Blob

from mlsriracha.interfaces.deploy import DeployInterface

class GcpVertexDeploy(DeployInterface):

    def __init__(self):
        print('Selected GCP Vertex profile')

        def getBucketNameFrom(gs_uri: str):
            bucket_start = -1
            for i in range(0, 2):
                bucket_start = gs_uri.find('/', bucket_start + 1)

            bucket_end = gs_uri.find('/', bucket_start + 1)
                
            # Printing nth occurrence
            # print ("Nth occurrence is at", val)

            bucket = gs_uri[bucket_start + 1: bucket_end]
            

            prefix = gs_uri[bucket_end + 1: len(gs_uri)]

            # chop off '/' at the end
            if prefix[len(prefix)-1: len(prefix)] == '/':
                prefix = prefix[0: len(prefix) - 1] 
            return bucket, prefix

        # create path for all model data
        Path('/opt/ml/model/').mkdir(parents=True, exist_ok=True)

        storage_client = storage.Client()

        gs_uri = os.getenv('AIP_STORAGE_URI')
        bucket, prefix=getBucketNameFrom(gs_uri)
        # chop off * for wildcard
        prefix = prefix.replace('*', '')
        print(f'bucket_name={bucket}')
        print(f'prefix={prefix}')
        # Note: Client.list_blobs requires at least package version 1.17.0.
        blobs = storage_client.list_blobs(bucket, prefix=prefix)

        # copy all
        for blob in blobs:
            print('Blob: {blob.name}')
            destination_uri = f'/opt/ml/model/{blob.name}' 
            blob.download_to_filename(destination_uri)

    def model_artifact(self, filename: str):
        """
        The path to model artifacts.

        Loads from the environmental variable that mlctl passes to Azure ML

        Arguments:
            filename (str): The name of the file which will be written back to S3

        Returns:
            path (str): The absolute path to the model output directory
        """
        return os.path.join(os.sep, 'opt', 'ml', 'model', filename)

    def endpoint_metadata(self):
        return {
            'container_port': os.getenv('AIP_HTTP_PORT'),
            'model_id': os.getenv('AIP_DEPLOYED_MODEL_ID')
        }