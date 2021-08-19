import unittest
import os

from base_class_V4test import TestBase
from base_class_V4test_online_deployment import TestBaseOnlineDeployment


class TestWMLClientWithKeras(TestBase, TestBaseOnlineDeployment, unittest.TestCase):
    deployment_name = "keras_deployment"
    model_name = "keras_model"
    sw_spec_name = 'default_py3.8'
    model_path = os.path.join('.', 'svt', 'artifacts', 'keras_model.h5.zip')

    def create_model(self, sw_spec_id) -> str:
        TestWMLClientWithKeras.logger.info("Creating keras model ...")

        self.logger.info("Publishing keras model ...")

        self.wml_client.repository.ModelMetaNames.show()

        model_props = {
            self.wml_client.repository.ModelMetaNames.NAME: self.model_name,
            self.wml_client.repository.ModelMetaNames.TYPE: "tensorflow_2.4",
            self.wml_client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sw_spec_id
        }
        published_model_details = self.wml_client.repository.store_model(TestWMLClientWithKeras.model_path,
                                                                         meta_props=model_props)  # , training_data=digits.data, training_target=digits.target)
        return self.wml_client.repository.get_model_uid(published_model_details)

    def get_scoring_payload(self):
        from keras.datasets import mnist

        from keras import backend as K

        batch_size = 128
        num_classes = 10
        epochs = 1

        # input shape
        img_rows, img_cols = 28, 28

        # samples to train
        num_train_samples = 500

        #        print(K._backend)

        # prepare train and test datasets
        (x_train, y_train), (x_test, y_test) = mnist.load_data()

        if K.image_data_format() == 'channels_first':
            x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
        else:
            x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)

        x_test = x_test.astype('float32')
        x_test /= 255
        print(x_test.shape[0], 'test samples')

        x_score_1 = x_test[23].tolist()
        x_score_2 = x_test[32].tolist()

        return [
            {
                'values': [x_score_1, x_score_2]
            }
        ]


if __name__ == '__main__':
    unittest.main()
