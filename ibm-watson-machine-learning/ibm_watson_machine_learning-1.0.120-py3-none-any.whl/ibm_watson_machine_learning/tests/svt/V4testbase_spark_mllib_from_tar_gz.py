import unittest
import os
import json
import logging

from base_class_V4test import TestBase
from base_class_V4test_online_deployment import TestBaseOnlineDeployment
from ibm_watson_machine_learning.tests.utils import get_wml_credentials, get_cos_credentials, get_space_id
from ibm_watson_machine_learning.tests.utils.cleanup import space_cleanup
from ibm_watson_machine_learning import APIClient


class TestWMLClientWithSpark(TestBase, TestBaseOnlineDeployment, unittest.TestCase):
    deployment_name = "spark_mllib_deployment"
    model_name = "spark_mllib_model"
    sw_spec_name = "spark-mllib_2.4"
    model_path = os.path.join('.', 'svt', 'artifacts', 'heart-drug-sample', 'drug-selection-model.tgz')
    pipeline_path = os.path.join('.', 'svt', 'artifacts', 'heart-drug-sample', 'drug-selection-pipeline.tgz')
    meta_path = os.path.join('.', 'svt', 'artifacts', 'heart-drug-sample', 'drug-selection-meta.json')

    def create_model(self, sw_spec_id) -> str:
        TestWMLClientWithSpark.logger.info("Publishing spark model ...")
        self.wml_client.repository.ModelMetaNames.show()

        model_props = {
            self.wml_client.repository.ModelMetaNames.NAME: self.model_name,
            self.wml_client.repository.ModelMetaNames.TYPE: "mllib_2.4",
            self.wml_client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sw_spec_id,
            self.wml_client.repository.ModelMetaNames.TRAINING_DATA_REFERENCES:
                [
                    {
                        'type': 's3',
                        'connection': {
                            'endpoint_url': 'not_applicable',
                            'access_key_id': 'not_applicable',
                            'secret_access_key': 'not_applicable'
                        },
                        'location': {
                            'bucket': 'not_applicable'
                        },
                        'schema': {
                            'id': '1',
                            'type': 'struct',
                            'fields': [{
                                'name': 'AGE',
                                'type': 'float',
                                'nullable': True,
                                'metadata': {
                                    'modeling_role': 'target'
                                }
                            }, {
                                'name': 'SEX',
                                'type': 'string',
                                'nullable': True,
                                'metadata': {}
                            }, {
                                'name': 'CHOLESTEROL',
                                'type': 'string',
                                'nullable': True,
                                'metadata': {}
                            }, {
                                'name': 'BP',
                                'type': 'string',
                                'nullable': True,
                                'metadata': {}
                            }, {
                                'name': 'NA',
                                'type': 'float',
                                'nullable': True,
                                'metadata': {}
                            }, {
                                'name': 'K',
                                'type': 'float',
                                'nullable': True,
                                'metadata': {}
                            }]
                        }
                    }
                ]}

        print('XXX' + str(model_props))
        published_model = self.wml_client.repository.store_model(model=self.model_path, meta_props=model_props)
        print("Model details: " + str(published_model))

        return self.wml_client.repository.get_model_uid(published_model)

    def get_scoring_payload(self):
        return [
            {
                "fields": ["AGE", "SEX", "BP", "CHOLESTEROL", "NA", "K"],
                "values": [[20.0, "F", "HIGH", "HIGH", 0.71, 0.07], [55.0, "M", "LOW", "HIGH", 0.71, 0.07]]
            }
        ]


if __name__ == '__main__':
    unittest.main()
