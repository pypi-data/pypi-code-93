import unittest
import os
from base_class_V4test import TestBase
from base_class_V4test_online_deployment import TestBaseOnlineDeployment


class TestAIFunction(TestBase, TestBaseOnlineDeployment, unittest.TestCase):
    deployment_name = "ai_function_deployment"
    model_name = "ai_function_model"
    function_filepath = os.path.join(os.getcwd(), 'svt', 'artifacts', 'ai_function.gz')
    sw_spec_name_cloud = 'default_py3.7'
    sw_spec_name_icp = 'default_py3.7_opence'

    def create_model(self, sw_spec_id) -> str:
        self.wml_client.repository.FunctionMetaNames.show()

        function_props = {
            self.wml_client.repository.FunctionMetaNames.NAME: self.model_name,
            self.wml_client.repository.FunctionMetaNames.DESCRIPTION: 'desc',
            self.wml_client.repository.FunctionMetaNames.SOFTWARE_SPEC_UID: sw_spec_id
        }

        ai_function_details = self.wml_client.repository.store_function(self.function_filepath, function_props)

        return self.wml_client.repository.get_function_uid(ai_function_details)

    def get_scoring_payload(self):
        return [{
            "fields": ["multiplication"],
            "values": [[2.0, 2.0], [99.0, 99.0]]
        }]


if __name__ == '__main__':
    unittest.main()
