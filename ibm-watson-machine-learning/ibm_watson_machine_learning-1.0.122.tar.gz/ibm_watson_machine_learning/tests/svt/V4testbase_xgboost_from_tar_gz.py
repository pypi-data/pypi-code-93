import unittest
import os

from base_class_V4test import TestBase
from base_class_V4test_online_deployment import TestBaseOnlineDeployment
from models_preparation import *


class TestWMLClientWithXGBoost(TestBase, TestBaseOnlineDeployment, unittest.TestCase):
    deployment_name = "xgboost_deployment"
    model_name = "xgboost_model"
    sw_spec_name = 'default_py3.8'
    model_path = os.path.join(os.getcwd(), 'svt', 'artifacts', 'xgboost_model.tar.gz')

    def create_model(self, sw_spec_id) -> str:
        TestWMLClientWithXGBoost.logger.info("Creating xgboost model ...")

        model_data = create_xgboost_model_data()
        TestWMLClientWithXGBoost.model = model_data['model']

        print()
        print(model_data['params'])
        predicted = model_data['prediction']

        TestWMLClientWithXGBoost.logger.info("Predicted values:")
        TestWMLClientWithXGBoost.logger.debug(predicted)
        self.assertIsNotNone(predicted)

        file_path = 'xgboost.pickle'

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
                           self.wml_client.repository.ModelMetaNames.TYPE: "xgboost_1.3",
                           self.wml_client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sw_spec_id
                           }
            published_model = self.wml_client.repository.store_model(model=self.model_path, meta_props=model_props)
            return self.wml_client.repository.get_model_uid(published_model)
        finally:
            os.remove(self.model_path)

    def get_scoring_payload(self):
        TestWMLClientWithXGBoost.logger.info("Online model scoring ...")

        import xgboost as xgb
        import scipy

        labels = []
        row = []
        col = []
        dat = []
        i = 0
        for l in open(os.path.join('svt', 'artifacts', 'agaricus.txt.test')):
            arr = l.split()
            labels.append(int(arr[0]))
            for it in arr[1:]:
                k, v = it.split(':')
                row.append(i)
                col.append(int(k))
                dat.append(float(v))
            i += 1
        csr = scipy.sparse.csr_matrix((dat, (row, col)))

        inp_matrix = xgb.DMatrix(csr)

        # print(TestWMLClientWithXGBoost.model.predict(inp_matrix))

        return [
            {
                'values': csr.getrow(0).toarray().tolist()
            }
        ]


if __name__ == '__main__':
    unittest.main()
