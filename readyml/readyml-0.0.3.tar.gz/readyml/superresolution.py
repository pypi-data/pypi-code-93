import tensorflow_hub as hub
import tensorflow as tf
from readyml.utils import fwks_init, model_utils

fwks_init.init_tensorflow()

class SuperResolution():

    def __init__(self, model_name):
        self.model = model_utils.load(model_name)

    def infer(self, low_resolution_image):
        low_resolution_image = tf.cast(low_resolution_image, tf.float32)
        low_resolution_image = tf.expand_dims(low_resolution_image, 0)
        return self.model(low_resolution_image)[0]

class ESRgan(SuperResolution):
    """
    Enhanced Super Resolution GAN (Wang et. al.)[1] for image super resolution. Produces x4 Super Resolution Image from images of {Height, Width} >=64. Works best on Bicubically downsampled images.\ (*This is because, the model is originally trained on Bicubically Downsampled DIV2K Dataset*)
    URL: https://tfhub.dev/captain-pool/esrgan-tf2/1
    """
    def __init__(self):
        super().__init__("esrgan-tf2")
