import numpy as np
from PIL import Image
import tensorflow as tf
from mirnet.model import mirnet_model
from mirnet.utils import closest_number
from readyml.utils import model_utils
import os.path
import pathlib, requests
from pathlib import Path

class MIRNet():
    def __init__(self):
        model_name = "mirnet_low_light_weights_best"
        self.model = self._load_model(model_name, num_rrg=3, num_mrb=2, channels=64)

    def _load_model(self, model_name, num_rrg: int, num_mrb: int, channels: int):

        model = mirnet_model(
            image_size=None, num_rrg=num_rrg,
            num_mrb=num_mrb, channels=channels
        )
        model_url = model_utils.model_utils_names.get(model_name)

        weights_folder = f"{Path.home()}/.cache/readyml/"
        if not os.path.exists(weights_folder):
            os.makedirs(weights_folder)

        weights_filename = f"{weights_folder}mirnet_low_light_weights_best.h5"
        if not os.path.exists(weights_filename):
            r = requests.get(model_url, allow_redirects=True, stream=True)

            with open(weights_filename, 'wb') as f:
                f.write(r.content)

        model.load_weights(weights_filename)
        return model

    def infer(self, original_image, image_resize_factor: float = 1.):
        width, height = original_image.size
        target_width, target_height = (
            closest_number(width // image_resize_factor, 4),
            closest_number(height // image_resize_factor, 4)
        )
        original_image = original_image.resize(
            (target_width, target_height), Image.ANTIALIAS
        )
        image = tf.keras.preprocessing.image.img_to_array(original_image)
        image = image.astype('float32') / 255.0
        image = np.expand_dims(image, axis=0)
        output = self.model.predict(image)
        output_image = output[0] * 255.0
        output_image = output_image.clip(0, 255)
        output_image = output_image.reshape(
            (np.shape(output_image)[0], np.shape(output_image)[1], 3)
        )
        output_image = Image.fromarray(np.uint8(output_image))
        original_image = Image.fromarray(np.uint8(original_image))
        return output_image
