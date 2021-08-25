import tensorflow as tf
from cross_framework_hpo.base_tensorflow_model import base_tensorflow_function

def vgg_tf_objective(config):
    model = tf.keras.applications.vgg16.VGG16(weights=None, input_shape=(3, 32, 32), classes=10)
    return base_tensorflow_function(config=config, model=model)

if __name__ == "__main__":
    test_config = {'batch_size': 532, 'learning_rate': 0.074552791, 'epochs': 26, 'adam_epsilon': 0.536216016}
    tf_test_acc, tf_model, tf_training_history = vgg_tf_objective(test_config)
    tf_model.save('../cifar10/vgg_lambda/dual_train_d24f6410' + 'tf_model')
    print("Accuracy is {}".format(tf_test_acc))