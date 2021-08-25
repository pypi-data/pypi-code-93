import numpy as np


def face2face_distance(em1, em2):
    return np.linalg.norm([em1] - em2, axis=1)

def face2face2_distance(em, list_em):
    return np.linalg.norm(list_em - em, axis=1)

def one2one_imgface(face1, face2, extractor='facenet'):
    pass

def one2many_imgface(face, list_face, extractor='facenet'):
    pass


