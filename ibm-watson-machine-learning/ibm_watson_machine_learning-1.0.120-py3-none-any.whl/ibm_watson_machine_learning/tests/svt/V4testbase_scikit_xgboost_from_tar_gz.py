import unittest
from sklearn.datasets import load_svmlight_file
from models_preparation import *

from base_class_V4test import TestBase
from base_class_V4test_online_deployment import TestBaseOnlineDeployment


class TestWMLClientWithXGBoost(TestBase, TestBaseOnlineDeployment, unittest.TestCase):
    deployment_name = "scikit_learn_deployment"
    model_name = "scikit_learn_model"
    sw_spec_name = 'default_py3.8'
    model_path = os.path.join('.', 'svt', 'artifacts', 'scikit_xgboost_model.tar.gz')

    def create_model(self, sw_spec_id) -> str:
        TestWMLClientWithXGBoost.logger.info("Publishing scikit-xgboost model ...")

        file_path = 'scikit_learn_xgboost.pickle'
        model_data = create_scikit_learn_xgboost_model_data()

        try:
            try:

                import pickle
                pickle.dump(model_data['model'], open(file_path, 'wb'))

                import tarfile
                import os.path

                with tarfile.open(self.model_path, "w:gz") as tar:
                    tar.add(file_path, arcname=os.path.basename(file_path))

            finally:
                os.remove(file_path)

            self.wml_client.repository.ModelMetaNames.show()

            model_props = {self.wml_client.repository.ModelMetaNames.NAME: self.model_name,
                           self.wml_client.repository.ModelMetaNames.TYPE: "scikit-learn_0.23",
                           self.wml_client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sw_spec_id
                           }
            published_model = self.wml_client.repository.store_model(model=self.model_path, meta_props=model_props)

        finally:
            os.remove(self.model_path)

        return self.wml_client.repository.get_model_uid(published_model)

    def get_scoring_payload(self):
        import os

        (X, _) = load_svmlight_file(os.path.join('svt', 'artifacts', 'agaricus.txt.test'))
        return [
            {
                'values': [list(X.toarray()[0, :])]
            }
        ]

if __name__ == '__main__':
    unittest.main()
