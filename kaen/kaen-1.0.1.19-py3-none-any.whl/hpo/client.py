import os
import time
import argparse
import random
from datetime import datetime

from laai.hpo.mlflow_utils import get_client, get_parent_run, get_active_child_run, assert_mlflow_tracking_uri, assert_mlflow_experiment_name

class BaseMLFlowClient():
    def on_run_start(self, run_idx, run):
        self.step = 0
        for i in range(10):
            loss = random.random()
            self.mlflow_client.log_metric(run.info.run_id, "loss", loss, step=i)
            self.mlflow_client.log_metric(run.info.run_id, "step", i, step=i)
            print(f"{run.info.run_id}: loss={loss}, step={i}")
    
    def on_run_terminated(self, run_idx, run):
        pass

    def run(self, num_runs = 1, mlflow_tracking_uri = None, mlflow_experiment_name = None):
        assert num_runs and isinstance(num_runs, int) and num_runs > 0, "The value of num_runs must be a positive integer."
        self.num_runs = num_runs

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

        #retrieve the experiement
        self.experiment = self.mlflow_client.get_experiment_by_name(mlflow_experiment_name)
        assert self.experiment, f"Unable to retrieve experiment named {mlflow_experiment_name} from {self.mlflow_tracking_uri}."

        parent_run = get_parent_run(self.mlflow_client, 
                                    self.experiment.name, 
                                    self.experiment.experiment_id)
        
        while num_runs \
                and parent_run \
                and 'RUNNING' == parent_run.info.status:
                    
            active_run = get_active_child_run(client = self.mlflow_client, 
                                                parent_run = parent_run)        
            if active_run:
                print(f"Starting {active_run}({active_run.info.status})")
                try:
                    seed = int(active_run.data.params['seed']) if 'seed' in active_run.data.params else int( datetime.now().microsecond )
                    print(f"{active_run}({active_run.info.status}) using seed={seed}")
                    random.seed(seed)

                    self.on_run_start(self.num_runs - num_runs, active_run)

                finally:
                    self.mlflow_client.set_terminated(active_run.info.run_id)
                    self.on_run_terminated(self.num_runs - num_runs, active_run)
                    print(f"Terminated {active_run.info.run_id}({active_run.info.status})")        

                    num_runs -= 1
                
            parent_run = get_parent_run(self.mlflow_client, self.experiment.name, self.experiment.experiment_id)

        if parent_run:
            print(f"Parent run status: {parent_run.info.status}, terminating...")
        else:
            print(f"Parent run unavailable, terminating...")    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start a client for an MLFlow based hyperparameter optimization service.')
    parser.add_argument('--num_runs', default = 1, type = int,
                        help='OPTIONAL: The number of the hyperparameter runs to execute as part of the experiment. Defaults to 1.')
                        
    args = parser.parse_args()

    client = BaseMLFlowClient()
    client.run( num_runs = int(args.num_runs) if isinstance(args.num_runs, int) else 1 )