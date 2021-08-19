import unittest
import os

from base_class_V4test import TestBase
from base_class_V4test_online_deployment import TestBaseOnlineDeployment


class TestWMLClientWithPMML(TestBase, TestBaseOnlineDeployment, unittest.TestCase):
    deployment_name = "pmml_deployment"
    model_name = "pmml_model"
    sw_spec_name = "spark-mllib_2.3"
    model_path = os.path.join('.', 'svt', 'artifacts', 'iris_chaid.xml')

    def create_model(self, sw_spec_id) -> str:
        self.logger.info("Publishing PMML model ...")

        self.wml_client.repository.ModelMetaNames.show()

        self.wml_client.software_specifications.list()

        model_props = {self.wml_client.repository.ModelMetaNames.NAME: self.model_name,
                       self.wml_client.repository.ModelMetaNames.TYPE: "pmml_4.2.1",
                       self.wml_client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sw_spec_id
                       }
        published_model_details = self.wml_client.repository.store_model(model=self.model_path, meta_props=model_props)
        return self.wml_client.repository.get_model_uid(published_model_details)

    def get_scoring_payload(self):
        return [
            {
                'fields': ['Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width'],
                'values': [[5.1, 3.5, 1.4, 0.2]]
            }
        ]


if __name__ == '__main__':
    unittest.main()
