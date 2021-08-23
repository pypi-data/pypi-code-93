import numpy as np
import logging


def emr(predicted, target, average):
    """Computes Exact Match Ratio

    Parameters
    ----------
    predicted : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
        predicted tensor
    target : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
        ground truth tensor
    average : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
        average tensor
    
    Returns
    -------
    `float <https://docs.python.org/3/library/functions.html#float>`_
        exact match ratio

    """
    logging.debug("Evaluating Exact-Match-Ratio(EMR)")
    return np.all(target == predicted, axis=1).mean()


def hamming(predicted, target, average):
    """Computes Hamming Distance

    Parameters
    ----------
    predicted : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
        predicted tensor
    target : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
        ground truth tensor
    average : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
        average tensor

    Returns
    -------
    `float <https://docs.python.org/3/library/functions.html#float>`_
        hamming distance

    """
    logging.debug("Evaluating Hamming loss")
    tmp = 0
    for i in range(target.shape[0]):
        tmp += np.size(target[i] == predicted[i]) - np.count_nonzero(target[i] == predicted[i])
    return tmp / (target.shape[0] * target.shape[1])
