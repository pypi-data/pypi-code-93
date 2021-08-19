import unittest
from sklearn.datasets import load_svmlight_file

from base_class_V4test import TestBase
from base_class_V4test_online_deployment import TestBaseOnlineDeployment
from models_preparation import *


class TestWMLClientWithXGBoost(TestBase, TestBaseOnlineDeployment, unittest.TestCase):
    deployment_name = "scikit_learn_deployment"
    model_name = "scikit_learn_model"
    sw_spec_name = 'default_py3.8'

    def create_model(self, sw_spec_id) -> str:
        TestWMLClientWithXGBoost.logger.info("Creating scikit-xgboost model ...")

        model_data = create_scikit_learn_xgboost_model_data()
        predicted = model_data['prediction']

        TestWMLClientWithXGBoost.logger.info("Predicted values: " + str(predicted))
        self.assertIsNotNone(predicted)

        TestWMLClientWithXGBoost.logger.info("Publishing scikit-xgboost model ...")

        self.wml_client.repository.ModelMetaNames.show()

        model_props = {self.wml_client.repository.ModelMetaNames.NAME: self.model_name,
                       self.wml_client.repository.ModelMetaNames.TYPE: "scikit-learn_0.23",
                       self.wml_client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sw_spec_id
                       }
        published_model = self.wml_client.repository.store_model(model=model_data['model'], meta_props=model_props)
        return self.wml_client.repository.get_model_uid(published_model)

    def get_scoring_payload(self):
        (X, _) = load_svmlight_file(os.path.join('svt', 'artifacts', 'agaricus.txt.test'))
        return [
            {
                'values': [list(X.toarray()[0, :])]
            }
        ]

if __name__ == '__main__':
    unittest.main()
