import mlflow
import os 

from mlsriracha.interfaces.metadata import MetadataInterface

# conversion to MLFlow required artifact type for model inference
class ModelWrapper(mlflow.pyfunc.PythonModel):
    def __init__(self, model):
        self.model = model
        
    def predict(self, context, model_input):
        return self.model.predict_proba(model_input)[:,1]

class MlFlowMetadata(MetadataInterface):

    def __init__(self):
        print('Selected MLFlow profile')
        mlflow.set_tracking_uri(os.environ['sriracha_mlflow_tracking_uri'])
        os.environ['MLFLOW_TRACKING_URI'] = os.environ['sriracha_mlflow_tracking_uri']

        # assumes user leverages outside MLFLow environment,
        # delete azure environment mlflow run id
        if os.environ.get('MLFLOW_RUN_ID') is not None:
            del os.environ['MLFLOW_RUN_ID']

        mlflow.set_experiment(os.environ['sriracha_experiment_name'])
        mlflow.start_run(run_name=os.environ['sriracha_run_name'])
        mlflow.set_tag('mlsriracha', '0.0.1')

    def log_param(self, params):
        for key, value in params.items():
            print('Params: ', key, ': ', value)
            mlflow.log_param(key, value)

    def log_metric(self, params):
        mlflow.log_metrics(params) 

    def log_artifact(self, object, type='model'):
        mlflow_model = ModelWrapper(object)
        mlflow.pyfunc.log_model(artifact_path=os.environ['sriracha_run_name'], python_model=mlflow_model)
        pass

    def finish():
        pass