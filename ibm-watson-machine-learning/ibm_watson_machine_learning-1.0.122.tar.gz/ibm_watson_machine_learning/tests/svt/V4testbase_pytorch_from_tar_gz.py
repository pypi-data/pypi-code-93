import unittest
import os

from base_class_V4test import TestBase
from base_class_V4test_online_deployment import TestBaseOnlineDeployment
import numpy as np


class TestWMLClientWithPyTorch(TestBase, TestBaseOnlineDeployment, unittest.TestCase):
    deployment_name = "pytorch_deployment"
    model_name = "pytorch_model"
    sw_spec_name = 'default_py3.8'
    model_path = os.path.join('.', 'svt', 'artifacts', 'mnist_pytorch.tar.gz')

    def create_model(self, sw_spec_id) -> str:
        TestWMLClientWithPyTorch.logger.info("Publishing pytorch model ...")

        self.wml_client.repository.ModelMetaNames.show()

        self.wml_client.software_specifications.list()

        model_props = {self.wml_client.repository.ModelMetaNames.NAME: self.model_name,
                       self.wml_client.repository.ModelMetaNames.TYPE: "pytorch-onnx_1.7",
                       self.wml_client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sw_spec_id
                       }
        published_model = self.wml_client.repository.store_model(model=self.model_path, meta_props=model_props)
        return self.wml_client.repository.get_model_uid(published_model)

    def get_scoring_payload(self):
        TestWMLClientWithPyTorch.logger.info("Online model scoring ...")
        # (X, _) = load_svmlight_file(os.path.join('svt', 'artifacts', 'mnist.npz'))
        dataset = np.load(os.path.join('svt', 'artifacts', 'mnist.npz'))
        X = dataset['x_test']

        score_0 = [X[0].tolist()]
        score_1 = [X[1].tolist()]

        return [
            {
                'values': [score_0, score_1]
            }
        ]

if __name__ == '__main__':
    unittest.main()
