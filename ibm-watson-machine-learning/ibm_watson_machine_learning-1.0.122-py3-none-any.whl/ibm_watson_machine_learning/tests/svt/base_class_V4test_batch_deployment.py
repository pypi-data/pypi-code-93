import unittest

import logging
import uuid
from ibm_watson_machine_learning.tests.utils import get_wml_credentials, get_cos_credentials, get_space_id, is_cp4d
from ibm_watson_machine_learning.tests.utils.cleanup import space_cleanup
from ibm_watson_machine_learning import APIClient


class TestBaseBatchDeployment:
    wml_client = None
    deployment_uid = None
    model_uid = None
    deployment_name = None
    space_id = None
    logger = logging.getLogger(__name__)

    def get_job_payload_ref(self) -> dict:
        raise NotImplemented()

    def test_02_01_create_deployment(self):
        TestBaseBatchDeployment.logger.info("Create deployment ...")
        global deployment
        deployment = self.wml_client.deployments.create(
            self.model_uid,
            meta_props={
                self.wml_client.deployments.ConfigurationMetaNames.NAME: "Test deployment",
                self.wml_client.deployments.ConfigurationMetaNames.BATCH: {},
                self.wml_client.deployments.ConfigurationMetaNames.HARDWARE_SPEC: {"name": "S", "num_nodes": 1}
            }
        )

        TestBaseBatchDeployment.logger.info("model_uid: " + self.model_uid)
        TestBaseBatchDeployment.logger.info("Batch deployment: " + str(deployment))
        TestBaseBatchDeployment.deployment_uid = self.wml_client.deployments.get_uid(deployment)
        self.assertTrue("batch" in str(deployment))

    def test_02_02_get_batch_deployment_details(self):
        TestBaseBatchDeployment.logger.info("Get deployment details ...")
        deployment_details = self.wml_client.deployments.get_details()
        self.assertTrue("Test deployment" in str(deployment_details))

        TestBaseBatchDeployment.logger.debug("Batch deployment: " + str(deployment_details))
        TestBaseBatchDeployment.deployment_uid = self.wml_client.deployments.get_uid(deployment)
        self.assertIsNotNone(TestBaseBatchDeployment.deployment_uid)

    def test_02_03_score_batch(self):
        TestBaseBatchDeployment.logger.info("Batch model scoring ...")

        job_payload_ref = self.get_job_payload_ref()

        TestBaseBatchDeployment.logger.debug("Scoring data: {}".format(
            job_payload_ref[self.wml_client.deployments.DecisionOptimizationMetaNames.INPUT_DATA]))
        job = self.wml_client.deployments.create_job(self.deployment_uid, meta_props=job_payload_ref)

        import time

        job_id = self.wml_client.deployments.get_job_uid(job)

        elapsed_time = 0
        while self.wml_client.deployments.get_job_status(job_id).get('state') != 'completed' and elapsed_time < 300:
            elapsed_time += 10
            time.sleep(10)
        if self.wml_client.deployments.get_job_status(job_id).get('state') == 'completed':
            job_details_do = self.wml_client.deployments.get_job_details(job_id)
            kpi = job_details_do['entity']['decision_optimization']['solve_state']['details']['KPI.Total Calories']
            print(f"KPI: {kpi}")
        else:
            print("Job hasn't completed successfully in 5 minutes.")

        TestBaseBatchDeployment.logger.debug("Prediction: " + str(job_details_do))
        self.assertTrue("output_data" in str(job_details_do))

    def test_02_04_delete_batch_deployment(self):
        TestBaseBatchDeployment.logger.info("Delete model deployment ...")
        self.wml_client.deployments.delete(TestBaseBatchDeployment.deployment_uid)



if __name__ == '__main__':
    unittest.main()
