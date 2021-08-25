from .utils import model_utils
from keras.models import load_model
import cv2
import numpy as np

facenet_model = None

def facenet_ext(face_img, model_path=None, image_size=160):
    global facenet_model
    if facenet_model is None:
        if model_path is None:
            facenet_model = model_utils.load_facenet()
        else:
            facenet_model = load_model(model_path)
    face_img = cv2.resize(face_img, (image_size,image_size)).astype('float32')
    mean, std = face_img.mean(), face_img.std()
    face_pixels = (face_img - mean) / std
    samples = np.expand_dims(face_pixels, axis=0)
    yhat = facenet_model.predict(samples)[0]
    return yhat
