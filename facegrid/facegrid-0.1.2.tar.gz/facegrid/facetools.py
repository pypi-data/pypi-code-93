from keras.backend import minimum
from mtcnn.mtcnn import MTCNN
import cv2
import numpy as np
from facegrid.utils import preprocess_input
from facegrid.vggface import VGGFace
from scipy.spatial.distance import cosine
import json
import os
import base64

detector = MTCNN()

"""getFaceFeatures function returns features of faces in the image passed as parameter"""
def getFaceFeatures(image):
  faces = detector.detect_faces(image)
  return faces

"""getFaces function extracts all the faces in image passed as parameter and returns a list of all the faces in the image"""
def getFaces(image):
  features = getFaceFeatures(image)
  face_list = []
  for feature in features:
    d = {}
    d["face"] = extractFace(image,feature)
    d["features"] = feature
    face_list.append(d)
  return face_list


"""createBbox function returns an image with bounding box around faces"""
def createBbox(image):
  faces = getFaceFeatures(image)
  for face in faces:
    bounding_box = face['box']
    keypoints = face['keypoints']
    cv2.rectangle(image,
                  (bounding_box[0],bounding_box[1]),
                  (bounding_box[0] + bounding_box[2],bounding_box[1] + bounding_box[3]),
                  (0,155,255),
                  2)
    cv2.circle(image,(keypoints['left_eye']),2,(0,155,255),2)
    cv2.circle(image,(keypoints['right_eye']),2,(0,155,255),2)
    cv2.circle(image,(keypoints['nose']),2,(0,155,255),2)
    cv2.circle(image,(keypoints['mouth_left']),2,(0,155,255),2)
    cv2.circle(image,(keypoints['mouth_right']),2,(0,155,255),2)
  return image


def extractFace(image,feature,resize = (224,224)):
  x1, y1, width, height = feature['box']
  x2, y2 = x1 + width, y1 + height
  face_boundary = image[y1:y2,x1:x2]
  face_image = cv2.resize(face_boundary,resize)
  return face_image


"""getEmbeddings function returns the embeddings of face features from the faces passed as parameter"""
def getEmbeddings(face):
  face = np.asarray(face,'float32')
  face = preprocess_input(face,version=2)
  face = np.expand_dims(face, axis=0)
  model = VGGFace(model='resnet50',include_top=False,input_shape=(224,224,3),pooling='avg')
  return model.predict(face)


"""verify function returns the result of the verification and also the confidence of verfication"""
def verify(face1,face2):
  score = cosine(getEmbeddings(face1),getEmbeddings(face2))
  if score <= 0.5:
    return {
      "result": 1,
      "confidence" : (0.5-score)/0.5
    }
  return {
    "result": 0,
    "confidence" : (score - 0.5)/0.5
  }

"""registeFace function stores the name and features of the face as key value pairs in db.json"""
def registerFace(image,name):
  faces = getFaces(image)
  if(len(faces) > 2):
    raise Exception('The image contains more than 1 faces')
  if(len(faces) == 0):
    raise Exception('The image contains no faces')
  features = getEmbeddings(faces[0]["face"])
  features = features[0].tobytes()
  if(not os.path.isfile('./db.json')):
    with open('db.json','w+') as db:
      json.dump({},db)
  with open('db.json', 'r+') as db:
    data = json.loads(db.read())
  encoded = base64.b64encode(features)
  data[name] = encoded.decode('ascii')
  with open("db.json", "w+") as db:
    json.dump(data, db)


"""findFace function searches db.json and finds the best match with the face of given image"""
def findFace(image):
  if(not os.path.isfile('./db.json')):
    with open('db.json','w+') as db:
      json.dump({},db)
  with open('db.json', 'r+') as db:
    data = json.loads(db.read())
  faces = getFaces(image)

  for face in faces:
    d_list = []
    face_features = getEmbeddings(face["face"])
    minimum = 1
    name = ""
    for k,v in data.items():
      decoded = base64.b64decode(data[k])
      embedding = np.frombuffer(decoded,'float32')
      score = cosine(embedding,face_features)
      if(score < minimum):
        minimum = score
        name = k
    d = {}
    if(minimum > 0.5):
        d["name"] = "unknown"
    else:
        d["name"] = name
    d["features"] = face["features"]
    d["score"] = minimum
    d_list.append(d)
    return d_list
      

# faces = [extract_face(image) for image in [image_1,image_2]]
