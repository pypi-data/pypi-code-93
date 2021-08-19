import tensorflow_hub as hub
import tensorflow as tf
from readyml.utils import model_utils

class ClassificationModel():

    def __init__(self, model_name):

        #url = model_utils.load_module(model_name)
        hub_url = model_utils.model_utils_names.get(model_name)

        encoder = hub.KerasLayer(hub_url, trainable=True)
        inputs = tf.keras.layers.Input(
            shape=[None, None, None, 3],
            dtype=tf.float32,
            name='image')
        outputs = encoder(dict(image=inputs))

        self.module = tf.keras.Model(inputs, outputs, name='movinet')

    def infer(self, frame):
        return self.module(frame)


class MovienetA5(ClassificationModel):
    def __init__(self):
        super().__init__("movinet-a5")
