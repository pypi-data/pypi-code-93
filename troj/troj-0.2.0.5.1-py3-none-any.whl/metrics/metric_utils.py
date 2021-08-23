import numpy as np


def get_pred_data(preds):
    """

    :param preds: predictions from object detection model.
    :return: the boxes, labels, and scores as tensors.
    """
    boxes = preds["boxes"].detach().cpu().numpy()
    labels = preds["labels"].detach().cpu().numpy()
    scores = preds["scores"].detach().cpu().numpy()
    return boxes, labels, scores


def compute_Lp_distance(x1, x2, p=np.inf):
    """
    compute Lp distance of a collection of images against another collection.

    :param x1: image collection 1
    :param x2: image collection 2
    :param p: p norm
    :return: tensor of distances
    """
    x1 = np.reshape(x1, (x1.shape[0], -1))
    x2 = np.reshape(x2, (x2.shape[0], -1))
    difference_vect = x1 - x2
    lp_distance = np.linalg.norm(difference_vect, p, axis=1)
    return lp_distance
