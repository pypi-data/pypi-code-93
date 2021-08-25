import cv2
import sys
from utils import model_utils 
from utils.mtcnntf.utils import detect_face
from utils.ultra_light import define_img_size, convert_locations_to_boxes, center_form_to_corner_form, predict
import tensorflow as tf
import numpy as np
import os
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

ssd_model           = None
ultra_model         = None
pnet, rnet, onet    = None, None, None
dlib_hog_model      = None
dlib_68_landmark    = None
dlib_cnn_model      = None


def ssd_detect(frame,threshold=0.7, align=False):
    '''
    input: rgb image
    output: boxes
    '''
    global ssd_model
    (h, w) = frame.shape[:2]
    t1,t2 = 0,0
    if w>h:
        frame300 = np.zeros((w,w,3))
        t1 = int((w-h)/2)
        frame300[t1:t1+h, :, :] = frame
        frame = frame300
    else:
        frame300 = np.zeros((h,h,3))
        t2 = int((h-w)/2)
        frame300[:, t2:t2+w, :] = frame
        frame = frame300
    (h, w) = frame.shape[:2]

    if ssd_model is None:
        ssd_model = model_utils.load_ssd_model()
    frame = frame.astype(np.uint8)
    imageBlob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], False, False)
    ssd_model.setInput(imageBlob)
    detections = ssd_model.forward()

    boxes = []
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > threshold:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            face = frame[startY:endY, startX:endX]
            (fH, fW) = face.shape[:2]
            box = (box - np.array([t2,t1,t2,t1])).astype("int")
            boxes.append([max(box[0],0), max(box[1],0), min(box[2],h), min(box[3],w)])

    return dlib_align(frame, boxes) if align is True else np.array(boxes)

input_size = [640,480]
witdh = input_size[0]
height = input_size[1]
priors = define_img_size(input_size)

image_mean = np.array([127, 127, 127])
image_std = 128.0
iou_threshold = 0.3
center_variance = 0.1
size_variance = 0.2

def ultra_light_detect(frame, threshold=0.9):
    global ultra_model
    if ultra_model == None:
        ultra_model = model_utils.load_ultra_model()
    rect = cv2.resize(frame, (witdh, height))
    rect = cv2.cvtColor(rect, cv2.COLOR_BGR2RGB)
    ultra_model.setInput(cv2.dnn.blobFromImage(rect, 1 / image_std, (witdh, height), 127))
    boxes, scores = ultra_model.forward(["boxes", "scores"])
    boxes = np.expand_dims(np.reshape(boxes, (-1, 4)), axis=0)
    scores = np.expand_dims(np.reshape(scores, (-1, 2)), axis=0)
    boxes = convert_locations_to_boxes(boxes, priors, center_variance, size_variance)
    boxes = center_form_to_corner_form(boxes)
    boxes, labels, probs = predict(frame.shape[1], frame.shape[0], scores, boxes, threshold)

    return np.array(boxes)

def mtcnn_detect(frame, align=False):
    '''
    input: rgb image
    output: boxes
    '''
    global pnet, rnet, onet
    if pnet is None or rnet is None or onet is None:
        
        pnet, rnet, onet = model_utils.load_mtcnn_model()
        # PNet(), RNet(), ONet()
        # pnet(tf.ones(shape=[1,  12,  12, 3]))
        # rnet(tf.ones(shape=[1,  24,  24 ,3]))
        # onet(tf.ones(shape=[1,  48,  48, 3]))
        # load_weights(pnet, "./det1.npy"), load_weights(rnet, "./det2.npy"), load_weights(onet, "./det3.npy")

    total_boxes, points = detect_face(frame, 20, pnet, rnet, onet, [0.6, 0.7, 0.7], 0.709)

    (h, w) = frame.shape[:2]
    results = []
    boxes = []
    for bbox, keypoints in zip(total_boxes, points.T):
        result = {
            'box': [int(max(bbox[0],0)), int(max(bbox[1],0)),
                    int(min(bbox[2],h)), int(min(bbox[3],w))],
            'confidence': bbox[-1],
            'keypoints': {
                'left_eye': (int(keypoints[0]), int(keypoints[5])),
                'right_eye': (int(keypoints[1]), int(keypoints[6])),
                'nose': (int(keypoints[2]), int(keypoints[7])),
                'mouth_left': (int(keypoints[3]), int(keypoints[8])),
                'mouth_right': (int(keypoints[4]), int(keypoints[9])),
            }
        }
        results.append(result)
        boxes.append(result['box'])

    return boxes, results

def dlib_hog_detect(frame, align=False):
    '''
    input: rgb image
    output: boxes
    '''
    global dlib_hog_model
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if dlib_hog_model is None:
        dlib_hog_model = model_utils.load_dlib_hog()
    faces = dlib_hog_model(gray, 1)
    boxes = []
    for result in faces:
        x = result.left()
        y = result.top()
        x1 = result.right()
        y1 = result.bottom()
        boxes.append([x,y,x1,y1])
    return boxes

def dlib_cnn_detect(frame, align=False):
    '''
    input: rgb image
    output: boxes
    '''
    global dlib_cnn_model
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    if dlib_cnn_model is None:
        dlib_cnn_model = model_utils.load_dlib_hog()
    faces = dlib_cnn_model(rgb, 1)
    boxes = []
    for result in faces:
        x = result.left()
        y = result.top()
        x1 = result.right()
        y1 = result.bottom()
        boxes.append([x,y,x1,y1])
    return boxes

def dlib_align(frame, boxes):
    if dlib_68_landmark is None:
        dlib_68_landmark = model_utils.load_dlib_68_landmark()
    
    bb = [dlib.rectangle(css[2], css[1], css[0], css[3]) for css in boxes]
    landmarks = [dlib_68_landmark(frame,box) for box in bb]

    boxes = []
    for landmark in landmarks:
        x1 = min([p.x for p in landmark.parts()])
        y1 = min([p.y for p in landmark.parts()])
        x2 = max([p.x for p in landmark.parts()])
        y2 = max([p.y for p in landmark.parts()])
        boxes.append([x1,y1,x2,y2])
    
    return boxes


def test(id_cam=0, func='ssd', align=False, show=True):
    assert func in ['ssd', 'mtcnn', 'dlib']
    cap = cv2.VideoCapture(id_cam)
    ret, _ = cap.read()
    while ret==True :
        ret, frame = cap.read()
        frame2 = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        boxes = []
        if func == 'ssd':
            boxes = ssd_detect(frame2, align=align)
        elif func == 'mtcnn':
            boxes, _ = mtcnn_detect(frame2, align=align)
        elif func== 'dlib':
            boxes = dlib_cnn_detect(frame2, align=align)
        else:
            print("Func select ssd, mtcnn, dlib")
            break

        if show:
            if len(boxes)>0:
                for box in boxes:
                    cv2.rectangle(frame, (box[0],box[1]), (box[2],box[3]), (0,255,0),thickness=2)
            cv2.imshow('Show', frame)
            k=cv2.waitKey(1)
            if k == ord('q'):
                break


if __name__ == "__main__":
    test(id_cam='rtsp://admin:Adm%40c3241g@10.1.18.37:554/Streaming/channels/101cmd', show=True, func='ssd', align=False)
