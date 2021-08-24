"""Preprocessing class for ARM Networks."""
import numpy as np
import tensorflow as tf
tf.compat.v1.disable_eager_execution()


class Preprocessor:
    """Speech commands preprocessor class."""

    def __init__(self):
        """Initialize preprocessor by spectrogram decoding tensorflow graph."""
        graph = tf.compat.v1.Graph()
        with graph.as_default():
            self.audio_node = tf.compat.v1.placeholder(shape=(16000, 1), dtype=tf.float32)
            self.sample_rate_node = tf.compat.v1.placeholder(dtype=tf.int32)
            audio_specrogram = tf.raw_ops.AudioSpectrogram(
                input=self.audio_node,
                window_size=640,
                stride=320,
                magnitude_squared=True,
            )
            self.mfcc = tf.raw_ops.Mfcc(
                spectrogram=audio_specrogram,
                sample_rate=self.sample_rate_node,
                upper_frequency_limit=4000,
                lower_frequency_limit=20,
                filterbank_channel_count=40,
                dct_coefficient_count=10,
            )

        self.session = tf.compat.v1.Session(graph=graph)

    def wav_to_tensor(self, data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Run session to infer preprocessing part of ARM Networks."""
        return self.session.run(self.mfcc, {
            self.audio_node: data,
            self.sample_rate_node: sample_rate
        })

    @staticmethod
    def decode_wav_file(filename: str):
        """Load a wav file and return sample_rate and numpy data of float64 type."""
        with tf.compat.v1.Session(graph=tf.compat.v1.Graph()) as sess:
            wav_filename_placeholder = tf.compat.v1.placeholder(tf.string, [])
            wav_loader = tf.compat.v1.read_file(wav_filename_placeholder)
            wav_decoder = tf.compat.v1.audio.decode_wav(wav_loader, desired_channels=1)
            res = sess.run(wav_decoder, feed_dict={wav_filename_placeholder: filename})
        return res.sample_rate, res.audio.flatten()
