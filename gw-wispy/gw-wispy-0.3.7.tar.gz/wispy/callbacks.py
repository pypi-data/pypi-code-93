import tensorflow as tf

# https://stackoverflow.com/questions/59563085/how-to-stop-training-when-it-hits-a-specific-validation-accuracy
class ThresholdCallback(tf.keras.callbacks.Callback):
    def __init__(self, val):
        super(ThresholdCallback, self).__init__()
        self.val = val

    def on_epoch_end(self, epoch, logs=None):
        if logs.get("loss") <= self.val:
            self.model.stop_training = True
