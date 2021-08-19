import pickle

from mlsriracha.plugins.awssagemaker.process import AwsSageMakerProcess
from mlsriracha.plugins.mlflow.metadata import MlFlowMetadata

class JobAdapter:
    def __init__(self,
        providers):

        print('This is a processing job')
        self.metadata_objs = []

        # add comma to make the array split work
        
        if providers is None:
            print('No providers were passed to sriracha, disabling in this run.')
            return
        elif providers.find(',') == -1:
            providers = [providers]
        else:
            providers = providers.split(',')

        # get list of providers added
        for provider in providers:
            
            try: provider
            except NameError: 
                raise RuntimeError(f'{str} is not a valid provider')

            if provider.lower() == 'awssagemaker':
                print('Using AWS SageMaker as a provider')
                self.provider_obj = AwsSageMakerProcess()
                self.provider_name = provider.lower()

            elif provider.lower() == 'mlflow':
                self.metadata_objs.append(MlFlowMetadata())

            else:
                raise RuntimeError(f'{provider} is not a valid provider')
    
    def get_hyperparameters(self):
        return self.provider_obj.get_hyperparameters()

    def get_env_vars(self):
        return self.provider_obj.get_env_vars()
            
    def input_as_dataframe(self, filename=None):
        return self.provider_obj.input_as_dataframe(filename=filename)

    def artifact_path(self, filename: str):
        return self.provider_obj.log_artifact(filename)

    def log_param(self, params):
        for metadata_obj in self.metadata_objs:
            metadata_obj.log_param(params)

    def log_artifact(self, artifact_object, artifact_type='model'):
        if artifact_type == 'model': 
            with open(self.artifact_path(filename='model.pkl'), 'wb') as stream:
                pickle.dump(artifact_object, stream)
        elif artifact_type == 'data': 
            artifact_object.to_csv(self.artifact_path(filename='data.csv'), index=False)

        for metadata_obj in self.metadata_objs:
            metadata_obj.log_artifact(artifact_object, artifact_type)

    def log_metric(self, params):
        for metadata_obj in self.metadata_objs:
            metadata_obj.log_metric(params) 

    def finish(self):
        return self.provider_obj.finish()