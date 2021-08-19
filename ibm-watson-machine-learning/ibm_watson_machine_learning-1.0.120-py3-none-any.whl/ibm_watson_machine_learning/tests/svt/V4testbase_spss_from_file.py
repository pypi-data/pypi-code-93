import unittest
import os

from base_class_V4test import TestBase
from base_class_V4test_online_deployment import TestBaseOnlineDeployment


class TestWMLClientWithSPSS(TestBase, TestBaseOnlineDeployment, unittest.TestCase):
    deployment_name = "spss_deployment"
    model_name = "spss_model"
    sw_spec_name = "spss-modeler_18.1"
    model_path = os.path.join('.', 'svt', 'artifacts', 'customer-satisfaction-prediction.str')

    def create_model(self, sw_spec_id) -> str:
        TestWMLClientWithSPSS.logger.info("Saving trained model in repo ...")
        TestWMLClientWithSPSS.logger.debug("Model path: {}".format(self.model_path))

        self.wml_client.repository.ModelMetaNames.show()

        self.wml_client.software_specifications.list()

        model_meta_props = {self.wml_client.repository.ModelMetaNames.NAME: self.model_name,
                            self.wml_client.repository.ModelMetaNames.TYPE: "spss-modeler_18.1",
                            self.wml_client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sw_spec_id
                            }
        published_model = self.wml_client.repository.store_model(model=self.model_path, meta_props=model_meta_props)
        return self.wml_client.repository.get_model_uid(published_model)

    def get_scoring_payload(self):
        return [
            {
                "fields": ["customerID", "gender", "SeniorCitizen", "Partner", "Dependents", "tenure",
                           "PhoneService", "MultipleLines", "InternetService", "OnlineSecurity", "OnlineBackup",
                           "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
                           "PaperlessBilling", "PaymentMethod", "MonthlyCharges", "TotalCharges", "Churn",
                           "SampleWeight"],
                "values":[["3638-WEABW", "Female", 0, "Yes", "No", 58, "Yes", "Yes", "DSL", "No", "Yes", "No", "Yes", "No", "No", "Two year", "Yes", "Credit card (automatic)", 59.9, 3505.1, "No", 2.768]]
            }
        ]


if __name__ == '__main__':
    unittest.main()
