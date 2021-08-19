import tensorflow as tf
#import tensorflow.compat.v1 as tf
from readyml.utils import model_utils


class FaceGeneration():
    """
    Image generator based on tensorflow reimplementation of Progressive GANs[1].
    Maps from a 512-dimensional latent space to images. During training, the latent space vectors were sampled from a normal distribution.
    Module takes <Tensor(tf.float32, shape=[?, 512])>, representing a batch of latent vectors as input, and outputs <Tensor(tf.float32, shape=[?, 128, 128, 3])> representing a batch of RGB images.
    URL: https://tfhub.dev/google/progan-128/1
    """
    def __init__(self, model_name="progan-128"):
        self.module = model_utils.load(model_name).signatures['default']

    def infer(self, num_samples=1, size=512):
        noise = tf.random.normal([num_samples, size])
        result = self.module(noise)['default']
        result = tf.image.convert_image_dtype(result, tf.uint8)
        return result
