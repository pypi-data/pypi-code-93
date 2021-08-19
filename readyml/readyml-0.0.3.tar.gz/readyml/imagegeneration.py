import io, os
from readyml.labels import labels_loader
from scipy.stats import truncnorm
import numpy as np
import tensorflow.compat.v1 as tf
from readyml.utils import model_utils


class ImageGenerationModel():
    def __init__(self, model_name):
        tf.disable_v2_behavior()
        tf.reset_default_graph()

        self.module = model_utils.load_module(model_name)
        inputs = {k: tf.placeholder(v.dtype, v.get_shape().as_list(), k)
                  for k, v in self.module.get_input_info_dict().items()}

        # Warmup
        self.output = self.module(inputs)
        self.input_z = inputs['z']
        self.input_y = inputs['y']
        self.input_trunc = inputs['truncation']

        self.dim_z = self.input_z.shape.as_list()[1]
        self.vocab_size = self.input_y.shape.as_list()[1]

        initializer = tf.global_variables_initializer()
        self.sess = tf.Session()
        self.sess.run(initializer)

    def _load_labels(self):
        raw_labels = labels_loader.get_labels('tfhub_biggan_categories')
        return json.loads(raw_labels)

    def _truncated_z_sample(self, batch_size, truncation=1., seed=None):
        state = None if seed is None else np.random.RandomState(seed)
        values = truncnorm.rvs(-2, 2, size=(batch_size,
                               self.dim_z), random_state=state)
        return truncation * values

    def _one_hot(self, index):
        index = np.asarray(index)
        if len(index.shape) == 0:
            index = np.asarray([index])
        assert len(index.shape) == 1
        num = index.shape[0]
        output = np.zeros((num, self.vocab_size), dtype=np.float32)
        output[np.arange(num), index] = 1
        return output

    def _one_hot_if_needed(self, label):
        label = np.asarray(label)
        if len(label.shape) <= 1:
            label = self._one_hot(label)
        assert len(label.shape) == 2
        return label

    def _sample(self, noise, label, truncation=1., batch_size=8):
        noise = np.asarray(noise)
        label = np.asarray(label)
        num = noise.shape[0]
        if len(label.shape) == 0:
            label = np.asarray([label] * num)
        if label.shape[0] != num:
            raise ValueError('Got # noise samples ({}) != # label samples ({})'
                             .format(noise.shape[0], label.shape[0]))
        label = self._one_hot_if_needed(label)
        ims = []
        for batch_start in range(0, num, batch_size):
            s = slice(batch_start, min(num, batch_start + batch_size))
            feed_dict = {self.input_z: noise[s],
                         self.input_y: label[s], self.input_trunc: truncation}
            ims.append(self.sess.run(self.output, feed_dict=feed_dict))
        ims = np.concatenate(ims, axis=0)
        assert ims.shape[0] == num
        ims = np.clip(((ims + 1) / 2.0) * 256, 0, 255)
        ims = np.uint8(ims)
        return ims

    def infer(self, category_num, num_samples=1, truncation=0.4, noise_seed=48):
        noise = self._truncated_z_sample(num_samples, truncation, noise_seed)
        return self._sample(noise, category_num, truncation=truncation)

    #def __del__(self):
    #    tf.enable_v2_behavior()


class BigGanDeep128(ImageGenerationModel):
    def __init__(self):
        super().__init__('biggan-deep-128')


class BigGanDeep256(ImageGenerationModel):
    def __init__(self):
        super().__init__('biggan-deep-256')


class BigGanDeep512(ImageGenerationModel):
    def __init__(self):
        super().__init__('biggan-deep-512')


class BigGan128(ImageGenerationModel):
    def __init__(self):
        super().__init__('biggan-128')


class BigGan256(ImageGenerationModel):
    def __init__(self):
        super().__init__('biggan-256')


class BigGan512(ImageGenerationModel):
    def __init__(self):
        super().__init__('biggan-512')        
