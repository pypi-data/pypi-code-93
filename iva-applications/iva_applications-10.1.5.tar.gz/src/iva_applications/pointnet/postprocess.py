# -*- coding=utf-8 -*-
""".Postprocessing for Pointnet."""
import numpy as np
from iva_applications.imagenet.postprocess import softmax

SHAPE_NAMES = ['airplane', 'bathtub', 'bed', 'bench', 'bookshelf', 'bottle', 'bowl', 'car',
               'chair', 'cone', 'cup', 'curtain', 'desk', 'door', 'dresser', 'flower_pot',
               'glass_box', 'guitar', 'keyboard', 'lamp', 'laptop', 'mantel', 'monitor', 'night_stand',
               'person', 'piano', 'plant', 'radio', 'range_hood', 'sink', 'sofa', 'stairs',
               'stool', 'table', 'tent', 'toilet', 'tv_stand', 'vase', 'wardrobe', 'xbox']


def get_name_from_list(vector: list) -> str:
    """
    Get name from list.

    Parameters
    ----------
    vector - output of network after postprocessing

    Returns - a name of a top1 class
    -------

    """
    name = SHAPE_NAMES[np.argmax(vector)]
    return name


def tensor_to_top_names(tensor: np.ndarray, top: int) -> np.ndarray:
    """
    Get top N values from tensor.

    Parameters
    ----------
    tensor - the output of the network that need to be postprocessed
    top - the number of classes need to be catched

    Returns - an np.ndarray of top highest classes
    -------

    """
    tensor = softmax(tensor.flatten())
    names_sorted = tensor.flatten().argsort()[::-1][:top]
    return names_sorted
