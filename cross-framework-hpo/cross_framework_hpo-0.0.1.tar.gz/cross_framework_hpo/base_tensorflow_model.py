import tensorflow as tf

def base_tensorflow_function(config, model):
    tf.random.set_seed(0)
    cifar = tf.keras.datasets.cifar10
    (x_train, y_train), (x_test, y_test) = cifar.load_data()
    x_train, x_test = x_train / 255.0, x_test / 255.0
    opt = tf.keras.optimizers.Adam(learning_rate=config['learning_rate'], epsilon=config['adam_epsilon'])

    model.compile(optimizer=opt,
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                  metrics=['accuracy'])

    res = model.fit(x_train, y_train, epochs=config['epochs'], batch_size=int(config['batch_size']), shuffle=False)
    training_loss_history = res.history['loss']
    res_test = model.evaluate(x_test, y_test)
    return res_test[1], model, training_loss_history