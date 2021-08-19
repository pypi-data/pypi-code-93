from mlsriracha.plugins.azureml.deploy import AzureMlDeploy
from mlsriracha.plugins.gcpvertex.deploy import GcpVertexDeploy
from mlsriracha.plugins.awssagemaker.deploy import AwsSageMakerDeploy

class DeployAdapter:
    def __init__(self, provider: str):
        self.provider_name = provider.lower()

        print('This is a prediction job')
        try: provider
        except NameError: 
            raise RuntimeError(f'{str} is not a valid provider')
        
        if provider.lower() == 'azureml':
            print('Using Azure ML as a provider')
            self.provider_obj = AzureMlDeploy()
        elif provider.lower() == 'gcpvertex':
            print('Using GCP Vertex as a provider')
            self.provider_obj = GcpVertexDeploy()
        elif provider.lower() == 'awssagemaker':
            print('Using AWS SageMaker as a provider')
            self.provider_obj = AwsSageMakerDeploy()
        else:
            raise RuntimeError(f'{str} is not a valid provider')

    def model_artifact(self, filename: str):
        return self.provider_obj.model_artifact(filename)

    def endpoint_metadata(self):
        return self.provider_obj.endpoint_metadata()