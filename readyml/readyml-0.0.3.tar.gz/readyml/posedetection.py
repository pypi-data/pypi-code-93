import tensorflow as tf
import numpy as np
import json

import readyml.utils.visualization_utils as viz_utils
from readyml.labels import labels_loader
from readyml.utils import fwks_init, model_utils

fwks_init.init_tensorflow()


class PoseDetection():
    def __init__(self, model_name):
        self.model = model_utils.load(model_name).signatures['serving_default']

    def infer(self, image_pil):
        image = np.array(image_pil)
        image = tf.expand_dims(image, axis=0)
        image = tf.cast(tf.image.resize_with_pad(image, 192, 192), dtype=tf.int32)
        output = self.model(image)['output_0']
        #output = np.array(output)
        return output.numpy() #json.dumps(output.numpy(), sort_keys=True, indent=4)

    def draw(self, image_pil, keypoint_with_scores):
        image = np.array(image_pil)
        display_image = tf.expand_dims(image, axis=0)
        display_image = tf.cast(tf.image.resize_with_pad(display_image, 1280, 1280), dtype=tf.int32)
        output_overlay = viz_utils.draw_prediction_on_image(
            np.squeeze(display_image.numpy(), axis=0),
            keypoint_with_scores)
        return output_overlay

class MovenetSingleposeLightning(PoseDetection):
    """
    URL: https://tfhub.dev/google/movenet/singlepose/lightning/4
    """
    def __init__(self):
        super().__init__("movenet-singlepose-lightning")
