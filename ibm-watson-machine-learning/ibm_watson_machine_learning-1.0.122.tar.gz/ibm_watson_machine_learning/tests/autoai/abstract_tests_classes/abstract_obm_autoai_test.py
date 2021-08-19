import abc
from os import environ

import unittest
import time

from sklearn.pipeline import Pipeline

from ibm_watson_machine_learning import APIClient
from ibm_watson_machine_learning.experiment import AutoAI
from ibm_watson_machine_learning.preprocessing import DataJoinGraph

from ibm_watson_machine_learning.deployment import WebService, Batch
from ibm_watson_machine_learning.workspace import WorkSpace
from ibm_watson_machine_learning.helpers.connections import DataConnection
from ibm_watson_machine_learning.experiment.autoai.optimizers import RemoteAutoPipelines
from ibm_watson_machine_learning.tests.utils import (get_wml_credentials, get_cos_credentials, get_space_id,
                                                     is_cp4d)
from ibm_watson_machine_learning.tests.utils.cleanup import space_cleanup, delete_model_deployment
from ibm_watson_machine_learning.utils.autoai.enums import PredictionType, RunStateTypes

from ibm_watson_machine_learning.tests.utils.assertions import get_and_predict_all_pipelines_as_lale, \
    validate_autoai_experiment

from ibm_watson_machine_learning.utils.autoai.utils import chose_model_output
from ibm_watson_machine_learning.preprocessing.data_join_pipeline import OBMPipelineGraphBuilder

get_step_details = OBMPipelineGraphBuilder.get_step_details
get_join_extractors = OBMPipelineGraphBuilder.get_join_extractors
get_extractor_columns = OBMPipelineGraphBuilder.get_extractor_columns
get_extractor_transformations = OBMPipelineGraphBuilder.get_extractor_transformations


class AbstractTestOBM(abc.ABC):
    """
    The abstract tests which covers:
    - training OBM+AutoAI model on a dataset
    - downloading all generated pipelines to lale pipeline
    In order to execute test connection definitions must be provided
    in inheriting classes.
    """

    bucket_name = environ.get('BUCKET_NAME', "wml-autoaitests-qa")
    pod_version = environ.get('KB_VERSION', None)
    space_name = environ.get('SPACE_NAME', 'regression_tests_sdk_space')

    cos_endpoint = "https://s3.us.cloud-object-storage.appdomain.cloud"
    results_cos_path = 'results_wml_autoai'

    # to be set in every child class:
    OPTIMIZER_NAME = "AutoAI + OBM regression test"

    SPACE_ONLY = True
    HISTORICAL_RUNS_CHECK = True
    BATCH_DEPLOYMENT_WITH_DF=False
    OBM=True

    experiment_info = dict(name=OPTIMIZER_NAME,
                           desc='test description',
                           prediction_type=PredictionType.MULTICLASS,
                           prediction_column='species',
                           autoai_pod_version=pod_version
                           )

    input_data_filenames: list = None
    input_data_path: str = None

    wml_client: 'APIClient' = None
    data_join_graph: 'DataJoinGraph' = None
    experiment: 'AutoAI' = None
    remote_auto_pipelines: 'RemoteAutoPipelines' = None
    wml_credentials = None
    cos_credentials = None
    pipeline_opt: 'RemoteAutoPipelines' = None
    service: 'WebService' = None
    service_batch: 'Batch' = None

    cos_resource_instance_id = None
    experiment_info: dict = None

    data_connections: list = None

    trained_pipeline_details = None
    run_id = None
    prev_run_id = None
    results_connection = None
    train_data = None

    pipeline: 'Pipeline' = None
    lale_pipeline = None
    deployed_pipeline = None
    hyperopt_pipelines = None
    new_pipeline = None
    new_sklearn_pipeline = None
    X_df = None
    X_values = None
    y_values = None

    project_id = None
    space_id = None

    asset_id = None
    connection_id = None

    @classmethod
    def setUpClass(cls) -> None:
        """
        Load WML credentials from config.ini file based on ENV variable.
        """
        cls.wml_credentials = get_wml_credentials()
        cls.wml_client = APIClient(wml_credentials=cls.wml_credentials.copy())

        cls.cos_credentials = get_cos_credentials()
        cls.cos_endpoint = cls.cos_credentials.get('endpoint_url')
        cls.cos_resource_instance_id = cls.cos_credentials.get('resource_instance_id')

        cls.project_id = cls.wml_credentials.get('project_id')

    def test_00a_space_cleanup(self):
        space_checked = False
        while not space_checked:
            space_cleanup(self.wml_client,
                          get_space_id(self.wml_client, self.space_name,
                                       cos_resource_instance_id=self.cos_resource_instance_id),
                          days_old=7)
            space_id = get_space_id(self.wml_client, self.space_name,
                                    cos_resource_instance_id=self.cos_resource_instance_id)
            try:
                self.assertIsNotNone(space_id, msg="space_id is None")
                space_checked = True
            except AssertionError:
                space_checked = False

        AbstractTestOBM.space_id = space_id

        if self.SPACE_ONLY:
            self.wml_client.set.default_space(self.space_id)
        else:
            self.wml_client.set.default_project(self.project_id)

    @abc.abstractmethod
    def test_01_create_multiple_data_connections__connections_created(self):
        # List of data connection: `data_connections`
        pass

    @abc.abstractmethod
    def test_02_create_data_join_graph__graph_created(self):
        pass
        # data_join_graph = DataJoinGraph()
        #
        # for f_name in self.input_data_filenames:
        #     data_join_graph.node(name=f_name.split('.')[0])
        # data_join_graph.edge(from_node="main", to_node="customers",
        #                      from_column=["group_customer_id"], to_column=["group_customer_id"])
        # data_join_graph.edge(from_node="main", to_node="transactions",
        #                      from_column=["transaction_id"], to_column=["transaction_id"])
        # data_join_graph.edge(from_node="main", to_node="purchase",
        #                      from_column=["group_id"], to_column=["group_id"])
        # data_join_graph.edge(from_node="transactions", to_node="products",
        #                      from_column=["product_id"], to_column=["product_id"])

        # TestOBMAndKB.data_join_graph = data_join_graph

    def test_03_data_join_graph_visualization(self):
        print("Visualizing data_join_graph...")
        self.data_join_graph.visualize()

    def test_04_initialize_AutoAI_experiment__pass_credentials__object_initialized(self):
        if self.SPACE_ONLY:
            AbstractTestOBM.experiment = AutoAI(wml_credentials=self.wml_credentials.copy(),
                                                space_id=self.space_id)
        else:
            AbstractTestOBM.experiment = AutoAI(wml_credentials=self.wml_credentials.copy(),
                                                project_id=self.project_id)

        self.assertIsInstance(self.experiment, AutoAI, msg="Experiment is not of type AutoAI.")

    def test_05_initialize_optimizer(self):
        # check if data_join_graph is in experiment info

        AbstractTestOBM.experiment_info = validate_autoai_experiment(self.experiment_info,
                                                                     self.pod_version,
                                                                     self.data_join_graph)

        self.assertIsNotNone(AbstractTestOBM.experiment_info.get("data_join_graph"))

        AbstractTestOBM.remote_auto_pipelines = self.experiment.optimizer(**AbstractTestOBM.experiment_info)

        self.assertIsInstance(self.remote_auto_pipelines, RemoteAutoPipelines,
                              msg="experiment.optimizer did not return RemoteAutoPipelines object")

    def test_06_get_configuration_parameters_of_remote_auto_pipeline(self):
        print("Getting experiment configuration parameters...")
        parameters = self.remote_auto_pipelines.get_params()
        print(parameters)
        self.assertIsInstance(parameters, dict, msg='Config parameters are not a dictionary instance.')

    def test_08_fit_run_training_of_auto_ai_in_wml(self):
        print("Scheduling OBM + KB training...")

        AbstractTestOBM.trained_pipeline_details = self.remote_auto_pipelines.fit(
            training_data_reference=self.data_connections,
            training_results_reference=self.results_connection,
            background_mode=False)

        AbstractTestOBM.run_id = self.trained_pipeline_details['metadata']['id']

        status = self.remote_auto_pipelines.get_run_status()
        run_details = self.remote_auto_pipelines.get_run_details().get('entity')
        self.assertNotIn(status, ['failed', 'canceled'], msg=f"Training finished with status {status}. \n"
                                                             f"Details: {run_details.get('status')}")

        # TestOBMAndKB.model_location = \
        #     self.trained_pipeline_details['entity']['status']['metrics'][-1]['context']['intermediate_model'][
        #         'location'][
        #         'model']
        # TestOBMAndKB.training_status = self.trained_pipeline_details['entity']['results_reference']['location'][
        #     'training_status']

        for connection in self.data_connections:
            self.assertIsNotNone(
                connection.auto_pipeline_params,
                msg=f'DataConnection auto_pipeline_params was not updated for connection: {connection.id}')

    def test_09_download_original_training_data(self):
        print("Downloading each training file...")
        for connection in self.remote_auto_pipelines.get_data_connections():
            train_data = connection.read()

            print(f"Connection: {connection.id} - train data sample:")
            print(train_data.head())
            self.assertGreater(len(train_data), 0)

    def test_10_download_preprocessed_obm_training_data(self):
        print("Downloading OBM preprocessed training data with holdout split...")
        AbstractTestOBM.train_data = (
            self.remote_auto_pipelines.get_preprocessed_data_connection().read())

        AbstractTestOBM.X_df = self.train_data.drop([self.experiment_info['prediction_column']], axis=1)[
                               :10]
        AbstractTestOBM.X_values = AbstractTestOBM.X_df.values
        AbstractTestOBM.y_values = self.train_data[self.experiment_info['prediction_column']][:10]

        print("OBM train data sample:")
        print(self.train_data.head())
        self.assertGreater(len(self.train_data), 0)

    def test_11_get_run_details(self):
        parameters = self.remote_auto_pipelines.get_run_details()
        import json
        print(json.dumps(self.wml_client.training.get_details(training_uid=parameters['metadata']['id']), indent=4))
        print(parameters)
        self.assertIsNotNone(parameters)

    def test_12_get_metrics(self):
        metrics = self.wml_client.training.get_metrics(self.run_id)
        self.assertIsNotNone(metrics)

    def test_13_visualize_obm_pipeline(self):
        print("Visualizing OBM model ...")
        AbstractTestOBM.data_join_pipeline = self.remote_auto_pipelines.get_preprocessing_pipeline()
        assert isinstance(self.data_join_pipeline._pipeline_json, list)

    def test_14_check_if_data_join_pipeline_graph_correct(self):

        pipeline_json = self.data_join_pipeline._pipeline_json
        graph = self.data_join_pipeline._graph_json

        step_types = [message['feature_engineering_components']['obm'][0]['step_type'] for message in pipeline_json]
        last_non_join_iteration = step_types.index('join')
        selection_iteration = step_types.index('feature selection') + 1
        join_iterations = [i + 1 for i, x in enumerate(step_types) if x == "join"]

        for message in pipeline_json:
            name, iteration, _ = get_step_details(message)
            self.assertTrue(str(iteration) in graph['nodes'])

            if 1 < iteration <= 2:
                self.assertTrue(str(iteration) in graph['edges'][str(iteration - 1)])
            elif iteration in join_iterations:
                self.assertTrue(str(iteration) in graph['edges'][str(last_non_join_iteration)])
                extractors = get_join_extractors(message)

                if extractors is None:
                    continue
                for ext, i in zip(extractors, range(len(extractors))):
                    ext_index = str(iteration) + str(i)
                    self.assertTrue(ext_index in graph['nodes'] and
                                    ext_index in ext_index in graph['edges'][str(iteration)])

                    columns = get_extractor_columns(extractors[ext])
                    transformations = get_extractor_transformations(extractors[ext])
                    for j, column in enumerate(columns):
                        col_index = str(iteration) + str(i) + str(j)
                        self.assertTrue(col_index in graph['nodes'] and col_index in graph['edges'][str(ext_index)])

                        for transformation in transformations:
                            self.assertTrue(transformation in graph['edges'][str(col_index)])
                            self.assertTrue(str(selection_iteration) in graph['edges'][str(transformation)])

            elif iteration > selection_iteration:
                self.assertTrue(str(iteration) in graph['edges'][str(iteration - 1)])

    def test_14_predict_using_fitted_pipeline(self):
        print("Make predictions on best pipeline...")
        predictions = self.remote_auto_pipelines.predict(
            X=self.X_values)
        print(predictions)
        self.assertGreater(len(predictions), 0)

    def test_15_summary_listing_all_pipelines_from_wml(self):
        pipelines_summary = self.remote_auto_pipelines.summary()
        print(pipelines_summary.to_string())

        self.assertGreater(len(pipelines_summary), 0, msg=f"Summary is empty:\n {pipelines_summary.to_string()}")
        if 'max_number_of_estimators' in self.experiment_info and self.experiment_info:
            nb_gen_pipelines = 4 * self.experiment_info['max_number_of_estimators']
            self.assertEqual(len(pipelines_summary), nb_gen_pipelines,
                             msg=f"Incorrect pipelines in summary:\n {pipelines_summary.to_string()}")

    def test_16__get_data_connections__return_a_list_with_data_connections_with_optimizer_params(self):
        print("Getting all data connections...")
        data_connections = self.remote_auto_pipelines.get_data_connections()
        self.assertIsInstance(data_connections, list, msg="There should be a list container returned")
        self.assertIsInstance(data_connections[0], DataConnection,
                              msg="There should be a DataConnection object returned")

    def test_17_get_pipeline_params_specific_pipeline_parameters(self):
        print("Getting details of Pipeline_1...")
        pipeline_params = self.remote_auto_pipelines.get_pipeline_details(pipeline_name='Pipeline_1')
        print(pipeline_params)

    def test_18__get_pipeline_params__fetch_best_pipeline_parameters__parameters_fetched_as_dict(self):
        print("Getting details of the best pipeline...")
        best_pipeline_params = self.remote_auto_pipelines.get_pipeline_details()
        print(best_pipeline_params)

    ########
    # LALE #
    ########

    def test_13_get_pipeline__load_lale_pipeline__pipeline_loaded(self):
        AbstractTestOBM.lale_pipeline = self.remote_auto_pipelines.get_pipeline()
        print(f"Fetched pipeline type: {type(self.lale_pipeline)}")
        self.assertWarnsRegex(Warning, "OBM",
                             msg="Warning (OBM pipeline support only for inspection and deployment) was not raised")
        print(f"Fetched pipeline type: {type(self.lale_pipeline)}")

        from lale.operators import TrainablePipeline
        self.assertIsInstance(self.lale_pipeline, TrainablePipeline)

    def test_14_get_all_pipelines_as_lale(self):
        get_and_predict_all_pipelines_as_lale(self.remote_auto_pipelines, self.X_values)

    def test_20__pretty_print_lale__checks_if_generated_python_pipeline_code_is_correct(self):
        pipeline_code = self.lale_pipeline.pretty_print()
        try:
            exec(pipeline_code)

        except Exception as exception:
            self.assertIsNone(
                exception,
                msg=f"Pretty print from lale pipeline was not successful \n\n Full pipeline code:\n {pipeline_code}")


    #################################
    #        HISTORICAL RUNS        #
    #################################

    def test_21_list_historical_runs_and_get_run_ids(self):
        if not self.HISTORICAL_RUNS_CHECK:
            self.skipTest("Skipping historical runs check.")
        runs_df = self.experiment.runs(filter=self.OPTIMIZER_NAME).list()
        print(runs_df)
        self.assertIsNotNone(runs_df)
        self.assertGreater(len(runs_df), 0)

        runs_completed_df = runs_df[runs_df.state == 'completed']

        if len(runs_completed_df) > 1:
            AbstractTestOBM.prev_run_id = runs_completed_df.run_id.iloc[1]  # prev run_id
            print("Random historical run_id: {}".format(AbstractTestOBM.prev_run_id))
            self.assertIsNotNone(AbstractTestOBM.prev_run_id)

    def test_22_get_params_of_last_historical_run(self):
        if not self.HISTORICAL_RUNS_CHECK:
            self.skipTest("Skipping historical runs check.")

        run_params = self.experiment.runs.get_params(run_id=self.run_id)
        self.assertIn('prediction_type', run_params,
                      msg="prediction_type field not fount in run_params. Run_params are: {}".format(run_params))

        AbstractTestOBM.historical_opt = self.experiment.runs.get_optimizer(self.run_id)
        self.assertIsInstance(self.historical_opt, RemoteAutoPipelines,
                              msg="historical_optimizer is not type RemoteAutoPipelines. It's type of {}".format(
                                  type(self.historical_opt)))

        train_data = self.historical_opt.get_data_connections()[0].read()

    def test_23_get_last_historical_pipeline_and_predict_on_historical_pipeline(self):
        if not self.HISTORICAL_RUNS_CHECK:
            self.skipTest("Skipping historical runs check.")

        print("Getting pipeline for last run_id={}".format(self.run_id))
        summary = self.historical_opt.summary()
        pipeline_name = summary.index.values[0]
        historical_pipeline = self.historical_opt.get_pipeline(pipeline_name,
                                                               astype=self.experiment.PipelineTypes.SKLEARN)
        print(type(historical_pipeline))
        predictions = historical_pipeline.predict(self.X_values)
        print(predictions)
        self.assertGreater(len(predictions), 0, msg="Empty predictions")

