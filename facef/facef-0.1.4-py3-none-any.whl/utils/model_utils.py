from keras.models import load_model
import os
import gdown
import cv2
import tensorflow as tf

import sys
sys.path.append('../')
from utils.mtcnntf.models import PNet, RNet, ONet, load_weights


model_dir = os.path.join(os.path.expanduser('~'), '.duyai/model')

def load_facenet():
    if os.path.exists(model_dir + '/facenet_keras2.h5') == False:
        gdown.download('https://drive.google.com/u/0/uc?id=1babjBFdPgfMOt18f0CzeKlmV_8hcWjbH&export=download', model_dir + '/facenet_keras2.h5', quiet=False)

    
    return load_model(model_dir + '/facenet_keras2.h5')

def load_ssd_model():
    if os.path.exists(model_dir + '/res10_ssd.caffemodel') == False:
        gdown.download('https://drive.google.com/u/0/uc?id=1p-O44DtUUO5lzmACFHhMAtaIfGQL2Fj_&export=download', model_dir + '/res10_ssd.caffemodel', quiet=False)

    if os.path.exists(model_dir + '/deploy.prototxt') == False:
        gdown.download('https://drive.google.com/u/0/uc?id=1iO2O5Fuvx_G9VMyCyj3nxGI_WJnRHKci&export=download', model_dir + '/deploy.prototxt', quiet=False)
    
    return cv2.dnn.readNetFromCaffe(model_dir + '/deploy.prototxt', model_dir + '/res10_ssd.caffemodel')

def load_ultra_model():
    if os.path.exists(model_dir + '/version-RFB-640.onnx') == False:
        gdown.download('https://drive.google.com/u/0/uc?id=1rY7K-lYrmKSXoPndGXoiipkKfimRK8dF&export=download',  model_dir + '/version-RFB-640.onnx', quiet=False)
    return cv2.dnn.readNetFromONNX(model_dir + '/version-RFB-640.onnx')

def load_mtcnn_model():
    if os.path.exists(model_dir + '/mtcnn') == False:
        os.mkdir(model_dir + '/mtcnn')
    
    if os.path.exists(model_dir + '/mtcnn/det1.npy') == False:
        gdown.download('https://drive.google.com/u/0/uc?id=1GTwUhB98INz_4kDxnRcUQhnLNDGQ28VE&export=download', model_dir + '/mtcnn/det1.npy', quiet=False)

    if os.path.exists(model_dir + '/mtcnn/det2.npy') == False:
        gdown.download('https://drive.google.com/u/0/uc?id=1YM2F05d9N6aU2Qy4ZD4cy5LxdylE6KgZ&export=download', model_dir + '/mtcnn/det2.npy', quiet=False)

    if os.path.exists(model_dir + '/mtcnn/det3.npy') == False:
        gdown.download('https://drive.google.com/u/0/uc?id=1wn3QfiTwOg63XcrVI-SdJB0-9ddQnUHV&export=download', model_dir + '/mtcnn/det3.npy', quiet=False)

    pnet, rnet, onet = PNet(), RNet(), ONet()
    pnet(tf.ones(shape=[1,  12,  12, 3]))
    rnet(tf.ones(shape=[1,  24,  24 ,3]))
    onet(tf.ones(shape=[1,  48,  48, 3]))
    load_weights(pnet, model_dir + '/mtcnn/det1.npy'), load_weights(rnet, model_dir + '/mtcnn/det2.npy'), load_weights(onet, model_dir + '/mtcnn/det3.npy')

    return pnet, rnet, onet

def load_dlib_hog():
    os.system('pip install dlib')
    import dlib
    return dlib.get_frontal_face_detector()

def load_dlib_cnn():
    os.system('pip install dlib')
    import dlib
    if os.path.exists(model_dir + '/mmod_human_face_detector.dat') == False:
        gdown.download('https://drive.google.com/u/0/uc?id=18iieTDtCWaW5_HHEqS0iPyZ4K8eRNn3d&export=download', model_dir + 'mmod_human_face_detector.dat', quiet=False)
    
    return dlib.cnn_face_detection_model_v1(model_dir + 'mmod_human_face_detector.dat')

def load_dlib_68_landmark():
    if os.path.exists(model_dir + '/shape_predictor_68_face_landmarks.dat') == False:
        gdown.download('https://drive.google.com/u/0/uc?id=1IZZGRwUQvCX6_Dvbmc4T-bHthD_Isj-p&export=download', model_dir + '/shape_predictor_68_face_landmarks.dat', quiet=False)
    
    return dlib.shape_predictor(model_dir + '/shape_predictor_68_face_landmarks.dat')

def get_deepsort():
    if os.path.exists(model_dir + '/mars_deepsort.pb') == False:
        gdown.download('https://drive.google.com/u/0/uc?id=1iSMmGwDHhQcYCaFxgwES8Xs7OM_iL9Ns&export=download', model_dir + '/mars_deepsort.pb', quiet=False)

def get_yolov3():
    if os.path.exists(model_dir + '/yolo3') == False:
        os.mkdir(model_dir + '/yolo3')

    if os.path.exists(model_dir + '/yolo3/yolov3.h5') == False:
        gdown.download('https://drive.google.com/u/0/uc?id=1Y1d5Db9_AE4Udn4IVrVkyt-eSx2taGda&export=download', model_dir + '/yolo3/yolov3.h5', quiet=False)
    
    if os.path.exists(model_dir + '/yolo3/yolo_anchors.txt') == False:
        gdown.download('https://drive.google.com/u/0/uc?id=17yA6ewzD8Zw-G05URC5kxvHer2tzyEVc&export=download', model_dir + '/yolo3/yolo_anchors.txt', quiet=False)
    
    if os.path.exists(model_dir + '/yolo3/coco_classes.txt') == False:
        gdown.download('https://drive.google.com/u/0/uc?id=1YRSDhZ2j9Y08vO6a2CMYi7umtOJHcwhG&export=download', model_dir + '/yolo3/coco_classes.txt', quiet=False)


