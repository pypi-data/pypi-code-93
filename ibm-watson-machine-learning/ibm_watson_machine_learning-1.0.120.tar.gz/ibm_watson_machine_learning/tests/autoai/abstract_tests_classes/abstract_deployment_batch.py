import abc
from os import environ

import unittest

from sklearn.pipeline import Pipeline

from ibm_watson_machine_learning import APIClient
from ibm_watson_machine_learning.deployment import Batch
from ibm_watson_machine_learning.workspace import WorkSpace
from ibm_watson_machine_learning.experiment.autoai.optimizers import RemoteAutoPipelines
from ibm_watson_machine_learning.helpers.connections import DataConnection, AssetLocation, DeploymentOutputAssetLocation
from ibm_watson_machine_learning.tests.utils import (get_wml_credentials, get_cos_credentials, get_space_id,
                                                     is_cp4d)
from ibm_watson_machine_learning.tests.utils.cleanup import space_cleanup, delete_model_deployment
from ibm_watson_machine_learning.utils.autoai.enums import TShirtSize, PredictionType


class AbstractTestBatch(abc.ABC):
    """
    The abstract tests which covers:
    - deployment with lale pipeline
    - deployment deletion
    In order to execute test connection definitions must be provided
    in inheriting classes.
    """
    SPACE_ONLY = True

    BATCH_DEPLOYMENT_WITH_DF = True
    BATCH_DEPLOYMENT_WITH_DA = True

    DEPLOYMENT_NAME = "SDK tests Deployment"

    wml_client: 'APIClient' = None
    remote_auto_pipelines: 'RemoteAutoPipelines' = None
    wml_credentials = None
    service_batch: 'Batch' = None

    asset_id = None
    batch_payload_location = None
    batch_output_filename = "batch_output.csv"

    space_id = None
    project_id = None
    target_space_id = None

    X_df = None

    @abc.abstractmethod
    def test_00a_space_cleanup(self):
        pass

    #########################
    #  Batch deployment
    #########################

    def test_41_batch_deployment_setup_and_preparation(self):
        # note: if target_space_id is not set, use the space_id
        if self.target_space_id is None:
            self.target_space_id = self.space_id
        # end note

        if self.SPACE_ONLY:
            AbstractTestBatch.service_batch = Batch(source_wml_credentials=self.wml_credentials,
                                                    source_space_id=self.space_id,
                                                    target_wml_credentials=self.wml_credentials,
                                                    target_space_id=self.target_space_id)
        else:
            AbstractTestBatch.service_batch = Batch(source_wml_credentials=self.wml_credentials,
                                                    source_project_id=self.project_id,
                                                    target_wml_credentials=self.wml_credentials,
                                                    target_space_id=self.target_space_id)

        self.assertIsInstance(AbstractTestBatch.service_batch, Batch, msg="Deployment is not of Batch type.")
        self.assertIsInstance(AbstractTestBatch.service_batch._source_workspace, WorkSpace,
                              msg="Workspace set incorrectly.")
        self.assertEqual(AbstractTestBatch.service_batch.id, None, msg="Deployment ID initialized incorrectly")
        self.assertEqual(AbstractTestBatch.service_batch.name, None, msg="Deployment name initialized incorrectly")

    def test_42_deploy__batch_deploy_best_computed_pipeline_from_autoai_on_wml(self):
        AbstractTestBatch.service_batch.create(
            experiment_run_id=self.remote_auto_pipelines._engine._current_run_id,
            model="Pipeline_2",
            deployment_name=self.DEPLOYMENT_NAME + ' BATCH')

        self.assertIsNotNone(AbstractTestBatch.service_batch.id, msg="Batch Deployment creation - missing id")
        self.assertIsNotNone(AbstractTestBatch.service_batch.id, msg="Batch Deployment creation - name not set")
        self.assertIsNotNone(AbstractTestBatch.service_batch.asset_id,
                             msg="Batch Deployment creation - model (asset) id missing, incorrect model storing")

    def test_43_score_batch_deployed_model(self):
        if self.BATCH_DEPLOYMENT_WITH_DF:
            scoring_params = AbstractTestBatch.service_batch.run_job(
                payload=self.X_df,
                background_mode=False)
            print(scoring_params)
            print(AbstractTestBatch.service_batch.get_job_result(scoring_params['metadata']['id']))
            self.assertIsNotNone(scoring_params)
            self.assertIn('predictions', str(scoring_params).lower())
        else:
            self.skipTest("Skip batch deployment run job with data frame")

    def test_44_list_batch_deployments(self):
        deployments = AbstractTestBatch.service_batch.list()
        print(deployments)
        self.assertIn('created_at', str(deployments).lower())
        self.assertIn('status', str(deployments).lower())

        params = AbstractTestBatch.service_batch.get_params()
        print(params)
        self.assertIsNotNone(params)

    def test_45a_run_job_batch_deployed_model_with_data_connection_data_asset(self):
        if self.batch_payload_location is None or not self.BATCH_DEPLOYMENT_WITH_DA:
            self.skipTest("Skip")
        else:
            self.wml_client.set.default_space(self.target_space_id)

            asset_details = self.wml_client.data_assets.create(
                name=self.batch_payload_location.split('/')[-1],
                file_path=self.batch_payload_location)
            AbstractTestBatch.asset_id = self.wml_client.data_assets.get_id(asset_details)

            payload_reference = DataConnection(location=AssetLocation(asset_id=AbstractTestBatch.asset_id))

            results_reference = DataConnection(
                location=DeploymentOutputAssetLocation(name=self.batch_output_filename))

            scoring_params = self.service_batch.run_job(
                payload=[payload_reference],
                output_data_reference=results_reference,
                background_mode=False)

            print(scoring_params)
            self.assertIsNotNone(scoring_params)

            self.wml_client.data_assets.list()

            data_asset_details = self.wml_client.data_assets.get_details()
            self.assertIn(self.batch_output_filename, str(data_asset_details))

    def test_45b_run_job_batch_deployed_model_with_data_connection_container(self):
        if self.wml_client.ICP or self.wml_client.WSD:
            self.skipTest("Batch Deployment with container data connection is available only for Cloud")
        else:
            self.skipTest("not ready")
        #     payload_reference = DataConnection(
        #         connection=S3Connection(endpoint_url=self.cos_endpoint,
        #                                 access_key_id=self.cos_credentials['cos_hmac_keys']['access_key_id'],
        #                                 secret_access_key=self.cos_credentials['cos_hmac_keys']['secret_access_key']),
        #         location=S3Location(bucket=self.bucket_name,
        #                             path=self.batch_payload_location.split('/')[-1])
        #     )
        #     results_reference = DataConnection(
        #         connection=S3Connection(endpoint_url=self.cos_endpoint,
        #                                 access_key_id=self.cos_credentials['cos_hmac_keys']['access_key_id'],
        #                                 secret_access_key=self.cos_credentials['cos_hmac_keys']['secret_access_key']),
        #         location=S3Location(bucket=self.bucket_name,
        #                             path='batch_output_car-price.csv')
        #     )
        #     payload_reference.write(data=self.batch_payload_location, remote_name=self.batch_payload_location.split('/')[-1])
        #
        # scoring_params = self.service_batch.run_job(
        #     payload=[payload_reference],
        #     output_data_reference=results_reference,
        #     background_mode=False)
        # print(scoring_params)
        # self.assertIsNotNone(scoring_params)
        # self.wml_client.data_assets.list()

    def test_49_delete_deployment_batch(self):
        print("Delete current deployment: {}".format(AbstractTestBatch.service_batch.deployment_id))
        AbstractTestBatch.service_batch.delete()
        self.wml_client.set.default_space(self.target_space_id) if not self.wml_client.default_space_id else None
        self.wml_client.repository.delete(AbstractTestBatch.service_batch.asset_id)
        if AbstractTestBatch.asset_id:
            self.wml_client.data_assets.delete(AbstractTestBatch.asset_id)
        self.assertEqual(AbstractTestBatch.service_batch.id, None, msg="Deployment ID deleted incorrectly")
        self.assertEqual(AbstractTestBatch.service_batch.name, None, msg="Deployment name deleted incorrectly")
        self.assertEqual(AbstractTestBatch.service_batch.scoring_url, None,
                         msg="Deployment scoring_url deleted incorrectly")
