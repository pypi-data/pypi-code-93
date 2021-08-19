import unittest
import os

from base_class_V4test import TestBase
from base_class_V4test_online_deployment import TestBaseOnlineDeployment
from models_preparation import create_tensorflow_model_data


class TestWMLClientWithTensorflow(TestBase, TestBaseOnlineDeployment, unittest.TestCase):
    deployment_name = "spss_deployment"
    model_name = "spss_model"
    sw_spec_name = 'tensorflow_2.4-py3.7'
    model_path = 'svt/artifacts/tf_iris_model'

    def create_model(self, sw_spec_id) -> str:
        res = create_tensorflow_model_data()
        TestWMLClientWithTensorflow.scoring_data = res['test_data']['x_test']

        try:
            import tensorflow as tf
            tf.saved_model.save(res['model'], self.model_path)

            TestWMLClientWithTensorflow.logger.info("Saving trained model in repo ...")
            TestWMLClientWithTensorflow.logger.debug(self.model_path)

            self.wml_client.repository.ModelMetaNames.show()

            model_meta_props = {self.wml_client.repository.ModelMetaNames.NAME: self.model_name,
                                self.wml_client.repository.ModelMetaNames.TYPE: "tensorflow_2.4",
                                self.wml_client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sw_spec_id
                                }
            published_model_details = self.wml_client.repository.store_model(model=self.model_path,
                                                                             meta_props=model_meta_props)
            return self.wml_client.repository.get_model_uid(published_model_details)
        finally:
            import shutil
            shutil.rmtree(self.model_path)

    def get_scoring_payload(self):
        return [
            {
                'values': self.scoring_data.tolist()
            }
        ]


if __name__ == '__main__':
    unittest.main()
