import unittest

from base_class_V4test import TestBase
from base_class_V4test_online_deployment import TestBaseOnlineDeployment
from models_preparation import *


class TestWMLClientWithSpark(TestBase, TestBaseOnlineDeployment, unittest.TestCase):
    deployment_name = "spark_mllib_deployment"
    model_name = "spark_mllib_model"
    sw_spec_name = "spark-mllib_2.4"

    def create_model(self, sw_spec_id) -> str:
        TestWMLClientWithSpark.logger.info("Creating spark model ...")

        model_data = create_spark_mllib_model_data()

        TestWMLClientWithSpark.logger.info("Publishing spark model ...")

        self.wml_client.repository.ModelMetaNames.show()

        model_props = {self.wml_client.repository.ModelMetaNames.NAME: self.model_name,
                       self.wml_client.repository.ModelMetaNames.TYPE: "mllib_2.4",
                       self.wml_client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sw_spec_id
                       }

        published_model = self.wml_client.repository.store_model(model=model_data['model'], meta_props=model_props,
                                                                 training_data=model_data['training_data'],
                                                                 pipeline=model_data['pipeline'])
        return self.wml_client.repository.get_model_uid(published_model)

    def get_scoring_payload(self):
        return [
            {
                "fields": ["GENDER", "AGE", "MARITAL_STATUS", "PROFESSION"],
                "values": [["M", 23, "Single", "Student"], ["M", 55, "Single", "Executive"]]
            }
        ]


if __name__ == '__main__':
    unittest.main()
