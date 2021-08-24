import tensorflow as tf
from ..layers.layers import TransLayer

class RucModel(tf.keras.models.Model):

    def __init__(self, features_columns):
        super(RucModel, self).__init__()
        self.trans_layer = TransLayer(features_columns)
        self.dense_layer = tf.keras.layers.Dense(49, activation='relu')
        self.dense_layer2 = tf.keras.layers.Dense(25, activation='relu')
        self.output_layer = tf.keras.layers.Dense(1, activation='sigmoid')

    @tf.function
    def train_step(self, data):
        x, y = data
        y = y['labels']
        with tf.GradientTape() as tape:
            y_pred = self(x, training=True)
            loss = self.compiled_loss(y, y_pred, regularization_losses=self.losses)

        trainable_vars = self.trainable_variables
        gradients = tape.gradient(loss, trainable_vars)

        self.optimizer.apply_gradients(zip(gradients, trainable_vars))
        self.compiled_metrics.update_state(y, y_pred)
        return {m.name: m.result() for m in self.metrics}

    @tf.function
    def test_step(self, data):
        x, y = data
        y = y['labels']

        y_pred = self(x, training=False)
        loss = self.compiled_loss(y, y_pred, regularization_losses=self.losses)
        self.compiled_metrics.update_state(y, y_pred)
        return {m.name: m.result() for m in self.metrics}

    def call(self, inputs):
        x = self.trans_layer(inputs)
        dly1_out = self.dense_layer(x)
        dly2_out = self.dense_layer2(dly1_out)
        out = self.output_layer(dly2_out)

        return out
