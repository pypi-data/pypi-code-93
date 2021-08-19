import unittest

import logging
import uuid
from ibm_watson_machine_learning.tests.utils import get_wml_credentials, get_cos_credentials, get_space_id, is_cp4d
from ibm_watson_machine_learning.tests.utils.cleanup import space_cleanup
from ibm_watson_machine_learning import APIClient


class TestBaseOnlineDeployment:
    wml_client = None
    deployment_uid = None
    model_uid = None
    scoring_url = None
    deployment_name = None
    space_id = None
    deployment_serving_name = None
    deployment_serving_name_patch = None
    logger = logging.getLogger(__name__)

    def get_scoring_payload(self):
        raise NotImplemented()

    def test_01_01_create_online_deployment(self):
        # if self.project_id:
        #     self.wml_client.set.default_space(self.space_id)

        TestBaseOnlineDeployment.deployment_serving_name = 'depl_serving_name_' + str(uuid.uuid4())[:8]
        TestBaseOnlineDeployment.deployment_serving_name_patch = 'depl_serving_name_patch_' + str(uuid.uuid4())[:8]

        deploy_meta = {
            self.wml_client.deployments.ConfigurationMetaNames.NAME: self.deployment_name,
            self.wml_client.deployments.ConfigurationMetaNames.DESCRIPTION: "deployment_description",
            self.wml_client.deployments.ConfigurationMetaNames.ONLINE: {}
        }

        TestBaseOnlineDeployment.logger.info("Create deployment")
        deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, meta_props=deploy_meta)
        TestBaseOnlineDeployment.logger.debug("deployment: " + str(deployment))
        TestBaseOnlineDeployment.scoring_url = self.wml_client.deployments.get_scoring_href(deployment)
        TestBaseOnlineDeployment.logger.debug("Scoring href: {}".format(TestBaseOnlineDeployment.scoring_url))
        TestBaseOnlineDeployment.deployment_uid = self.wml_client.deployments.get_uid(deployment)
        TestBaseOnlineDeployment.logger.debug("Deployment uid: {}".format(TestBaseOnlineDeployment.deployment_uid))
        self.wml_client.deployments.list()
        self.assertTrue(self.deployment_name in str(deployment))

    def test_01_02_serving_name_test(self):
        deployment_details = self.wml_client.deployments.get_details(serving_name='non_existing')
        self.assertTrue(len(deployment_details['resources']) == 0)

        self.wml_client.deployments.update(self.deployment_uid, {'serving_name': self.deployment_serving_name})

        deployment_details = self.wml_client.deployments.get_details(serving_name=self.deployment_serving_name)
        self.assertTrue(len(deployment_details['resources']) == 1)

        self.assertTrue(str(self.wml_client.deployments.get_serving_href(deployment_details['resources'][0])).endswith(
            f'/{self.deployment_serving_name}/predictions'))

        self.wml_client.deployments.update(self.deployment_uid, {'serving_name': self.deployment_serving_name_patch})

        deployment_details = self.wml_client.deployments.get_details(serving_name=self.deployment_serving_name)
        self.assertTrue(len(deployment_details['resources']) == 0)

        deployment_details = self.wml_client.deployments.get_details(serving_name=self.deployment_serving_name_patch)
        self.assertTrue(len(deployment_details['resources']) == 1)

        self.assertTrue(str(self.wml_client.deployments.get_serving_href(deployment_details['resources'][0])).endswith(
            f'/{self.deployment_serving_name_patch}/predictions'))

    def test_01_03_update_deployment(self):
        patch_meta = {
            self.wml_client.deployments.ConfigurationMetaNames.DESCRIPTION: "deployment_Updated_Function_Description",
        }
        self.wml_client.deployments.update(TestBaseOnlineDeployment.deployment_uid, patch_meta)

    def test_01_04_get_deployment_details(self):
        TestBaseOnlineDeployment.logger.info("Get deployment details")
        deployment_details = self.wml_client.deployments.get_details()
        TestBaseOnlineDeployment.logger.debug("Deployment details: {}".format(deployment_details))
        self.assertTrue(self.deployment_name in str(deployment_details))

    def test_01_05_score(self):
        predictions = self.wml_client.deployments.score(TestBaseOnlineDeployment.deployment_uid, {
            self.wml_client.deployments.ScoringMetaNames.INPUT_DATA: self.get_scoring_payload()})
        print("Predictions: {}".format(predictions))
        self.assertTrue("values" in str(predictions))

    def test_01_06_delete_deployment(self):
        TestBaseOnlineDeployment.logger.info("Delete deployment")
        self.wml_client.deployments.delete(TestBaseOnlineDeployment.deployment_uid)


if __name__ == '__main__':
    unittest.main()
