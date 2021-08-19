import unittest

import logging
from ibm_watson_machine_learning.tests.utils import get_wml_credentials, get_cos_credentials, get_space_id, is_cp4d
from ibm_watson_machine_learning.tests.utils.cleanup import space_cleanup
from ibm_watson_machine_learning import APIClient


class TestBase:
    wml_client = None
    model_uid = None
    space_name = 'tests_sdk_space'
    cos_resource_instance_id = None
    space_id = None
    model_name = None
    sw_spec_name = None
    sw_spec_name_cloud = None
    sw_spec_name_icp = None
    logger = logging.getLogger(__name__)

    def create_model(self, sw_spec_id: str) -> str:
        raise NotImplemented()

    @classmethod
    def setUpClass(cls) -> None:
        """
        Load WML credentials from config.ini file based on ENV variable.
        """

        cls.wml_credentials = get_wml_credentials()

        cls.wml_client = APIClient(wml_credentials=cls.wml_credentials)

        if not cls.wml_client.ICP:
            cls.cos_credentials = get_cos_credentials()
            cls.cos_endpoint = cls.cos_credentials.get('endpoint_url')
            cls.cos_resource_instance_id = cls.cos_credentials.get('resource_instance_id')

        cls.wml_client = APIClient(wml_credentials=cls.wml_credentials)
        cls.project_id = cls.wml_credentials.get('project_id')

    def test_00_00_space_cleanup(self):
        space_cleanup(self.wml_client,
                      get_space_id(self.wml_client, self.space_name,
                                   cos_resource_instance_id=self.cos_resource_instance_id),
                      days_old=7)
        TestBase.space_id = get_space_id(self.wml_client, self.space_name,
                                                            cos_resource_instance_id=self.cos_resource_instance_id)

        # if self.project_id:
        #     self.wml_client.set.default_project(self.project_id)
        # else:

        self.wml_client.set.default_space(self.space_id)

    def test_00_01_create_model(self):
        self.wml_client.software_specifications.list()
        if self.sw_spec_name:
            sw_spec_id = self.wml_client.software_specifications.get_id_by_name(self.sw_spec_name)
        else:
            if is_cp4d():
                sw_spec_id = self.wml_client.software_specifications.get_id_by_name(self.sw_spec_name_icp)
            else:
                sw_spec_id = self.wml_client.software_specifications.get_id_by_name(self.sw_spec_name_cloud)

        TestBase.model_uid = self.create_model(sw_spec_id)
        TestBase.logger.info("Model ID:" + str(TestBase.model_uid))
        self.assertIsNotNone(TestBase.model_uid)

    def test_00_02_update_model(self):
        artifact_type = self.wml_client.repository._check_artifact_type(self.model_uid)

        if artifact_type == 'model':
            model_props = {
                self.wml_client.repository.ModelMetaNames.DESCRIPTION: 'desc',
            }

            details = self.wml_client.repository.update_model(self.model_uid, model_props)
        elif artifact_type == 'function':
            function_props = {
                self.wml_client.repository.FunctionMetaNames.DESCRIPTION: 'desc',
            }

            details = self.wml_client.repository.update_function(self.model_uid, function_props)

    def test_00_03_download_model_content(self):
        try:
            import os
            os.remove('test_model_downloaded.gz')
        except:
            pass
        self.wml_client.repository.download(TestBase.model_uid, filename='test_model_downloaded.gz')
        try:
            os.remove('test_model_downloaded.gz')
        except:
            pass

    def test_00_04_get_details(self):
        details = self.wml_client.repository.get_details(self.model_uid)
        print(details)
        self.assertTrue(self.model_name in str(details))

    def test_00_05_list(self):
        self.wml_client.repository.list()

    def test_03_01_delete_model(self):
        TestBase.logger.info("Delete model")
        self.wml_client.repository.delete(TestBase.model_uid)



if __name__ == '__main__':
    unittest.main()
