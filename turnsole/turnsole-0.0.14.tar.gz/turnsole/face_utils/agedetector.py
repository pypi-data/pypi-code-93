# -*- coding: utf-8 -*-
# @Author        : lk
# @Email         : 9428.al@gmail.com
# @Create Date   : 2021-08-11 17:10:16
# @Last Modified : 2021-08-12 16:14:53
# @Description   : 

import os
import tensorflow as tf

class AgeDetector:
    def __init__(self, model_path):
        self.age_map = {
                        0: '0-2',
                        1: '4-6',
                        2: '8-13',
                        3: '15-20',
                        4: '25-32',
                        5: '38-43',
                        6: '48-53',
                        7: '60+'
                    }

        self.model = tf.keras.models.load_model(filepath=model_path,
                                                compile=False)
        self.inference_model = self.build_inference_model()

    def build_inference_model(self):
        image = self.model.input
        x = tf.keras.applications.mobilenet_v2.preprocess_input(image)
        predictions = self.model(x, training=False)
        inference_model = tf.keras.Model(inputs=image, outputs=predictions)
        return inference_model

    def predict_batch(self, images):
        # 输入一个人脸图片列表,列表不应为空
        images = tf.stack([tf.image.resize(image, [96, 96]) for image in images], axis=0)
        preds = self.inference_model.predict(images)
        indexes = tf.argmax(preds, axis=-1)
        classes = [self.age_map[index.numpy()] for index in indexes]
        return classes

if __name__ == '__main__':

    import cv2
    from turnsole import paths

    age_det = AGE_DETECTION(model_path='./ckpt/age_detector.h5')

    data_dir = '/home/lk/Project/Face_Age_Gender/data/Emotion/emotion/010003_female_yellow_22'

    for image_path in paths.list_images(data_dir):
        image = cv2.imread(image_path)
        classes = age_det.predict_batch([image])

        print(classes)

