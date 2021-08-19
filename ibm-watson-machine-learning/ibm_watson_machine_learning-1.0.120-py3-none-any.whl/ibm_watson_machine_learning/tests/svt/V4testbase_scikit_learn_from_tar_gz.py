import unittest
from sklearn import datasets

from base_class_V4test import TestBase
from base_class_V4test_online_deployment import TestBaseOnlineDeployment
from models_preparation import *


class TestWMLClientWithScikitLearn(TestBase, TestBaseOnlineDeployment, unittest.TestCase):
    deployment_name = "scikit_learn_deployment"
    model_name = "scikit_learn_model"
    sw_spec_name = 'default_py3.8'
    model_path = os.path.join(os.getcwd(), 'svt', 'artifacts', 'scikit_model.tar.gz')

    def create_model(self, sw_spec_id) -> str:
        TestWMLClientWithScikitLearn.logger.info("Publish model")
        file_path = 'scikit_learn.pickle'

        global digits
        digits = datasets.load_digits()

        try:

            try:

                TestWMLClientWithScikitLearn.logger.info("Creating scikit-learn model ...")

                model_data = create_scikit_learn_model_data()
                predicted = model_data['prediction']

                TestWMLClientWithScikitLearn.logger.debug(predicted)
                self.assertIsNotNone(predicted)

                import pickle
                pickle.dump(model_data['model'], open(file_path, 'wb'))

                import tarfile
                import os.path

                with tarfile.open(self.model_path, "w:gz") as tar:
                    tar.add(file_path, arcname=os.path.basename(file_path))

            finally:
                try:
                    os.remove(file_path)
                except:
                    pass

            self.logger.info("Publishing scikit-learn model ...")

            self.wml_client.repository.ModelMetaNames.show()

            model_props = {self.wml_client.repository.ModelMetaNames.NAME: self.model_name,
                           self.wml_client.repository.ModelMetaNames.TYPE: "scikit-learn_0.23",
                           self.wml_client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sw_spec_id
                           }
            published_model_details = self.wml_client.repository.store_model(model=self.model_path, meta_props=model_props,
                                                                         training_data=digits.data,
                                                                         training_target=digits.target)

        finally:
            try:
                os.remove(self.model_path)
            except:
                pass

        return self.wml_client.repository.get_model_uid(published_model_details)

    def get_scoring_payload(self):
        return [
            {
                'values': [
                    [0.0, 0.0, 5.0, 16.0, 16.0, 3.0, 0.0, 0.0, 0.0, 0.0, 9.0, 16.0, 7.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                     12.0, 15.0, 2.0, 0.0, 0.0, 0.0, 0.0, 1.0, 15.0, 16.0, 15.0, 4.0, 0.0, 0.0, 0.0, 0.0, 9.0, 13.0,
                     16.0, 9.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 14.0, 12.0, 0.0, 0.0, 0.0, 0.0, 5.0, 12.0, 16.0, 8.0,
                     0.0, 0.0, 0.0, 0.0, 3.0, 15.0, 15.0, 1.0, 0.0, 0.0],
                    [0.0, 0.0, 6.0, 16.0, 12.0, 1.0, 0.0, 0.0, 0.0, 0.0, 5.0, 16.0, 13.0, 10.0, 0.0, 0.0, 0.0, 0.0,
                     0.0, 5.0, 5.0, 15.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8.0, 15.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                     13.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.0, 16.0, 9.0, 4.0, 1.0, 0.0, 0.0, 3.0, 16.0, 16.0, 16.0,
                     16.0, 10.0, 0.0, 0.0, 5.0, 16.0, 11.0, 9.0, 6.0, 2.0]]
            }
        ]

if __name__ == '__main__':
    unittest.main()
