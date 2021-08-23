import numpy as np
import math
import logging


def fast_hist(predicted, target, num_classes):
    logging.debug("Inside fast_hist routine")
    k = (predicted >= 0) & (target < num_classes)
    return np.bincount(num_classes * predicted[k].astype(np.uint8) + target[k],
                       minlength=num_classes**2).reshape(num_classes, num_classes)


def cal_kappa(hist):
    logging.debug("Enter cal_kappa routine")
    if hist.sum() == 0:
        po = 0
        pe = 1
        kappa = 0
    else:
        po = np.diag(hist).sum() / hist.sum()
        pe = np.matmul(hist.sum(1), hist.sum(0).T) / hist.sum() ** 2
        if pe == 1:
            kappa = 0
        else:
            kappa = (po - pe) / (1 - pe)
    logging.debug("Exit cal_kappa routine")
    return kappa


def mIoU_and_SeK(predicted, target, num_classes):
    """Computes mean Intersection over Union (mIoU) and Separated Kappa (SeK) coeffifients

    Parameters
    ----------
    predicted : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
        predicted tensor
    target : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
        ground truth tensor
    num_classes : `int <https://docs.python.org/3/library/functions.html#int>`_
        number of classes

    Returns
    -------
    `float <https://docs.python.org/3/library/functions.html#float>`_, `float <https://docs.python.org/3/library/functions.html#float>`_
        mIoU, Sek values
    """
    logging.debug("Enter mIoU_and_SeK routine")
    hist = fast_hist(predicted.flatten(), target.flatten(), num_classes)
    hist_fg = hist[1:, 1:]
    c2hist = np.zeros((2, 2))
    c2hist[0][0] = hist[0][0]
    c2hist[0][1] = hist.sum(1)[0] - hist[0][0]
    c2hist[1][0] = hist.sum(0)[0] - hist[0][0]
    c2hist[1][1] = hist_fg.sum()
    hist_n0 = hist.copy()
    hist_n0[0][0] = 0
    kappa_n0 = cal_kappa(hist_n0)
    iu = np.diag(c2hist) / (c2hist.sum(1) + c2hist.sum(0) - np.diag(c2hist))
    IoU_fg = iu[1]
    IoU_mean = (iu[0] + iu[1]) / 2
    Sek = (kappa_n0 * math.exp(IoU_fg)) / math.e

    logging.debug("Exit mIoU_and_SeK routine")
    return IoU_mean, Sek


def mIoU(predicted, target, num_classes):
    """Computes Intersection over Union (mIoU) coefficient 

    For a confusion matrix, :math:`mIOU` is computed as:

    .. math:: mIOU = \\frac{1}{2} ( IOU_1 + IOU_2 )

    where :math:`IOU_1` measures identification of non-change pixel regions, and is computed as:

    .. math:: IOU_1 = q_{11}/(\sum\limits_{i=1}^{C} q_{i1} + \sum\limits_{j=1}^{C} q_{1j} - q_{11}) 
    
    and :math:`IOU_2` evaluates extraction of changed regions, and is computed as:

    .. math:: IOU_2 = \sum\limits_{i=2}^{C} \sum\limits_{j=2}^{C} q_{ij}/(\sum\limits_{i=1}^{C} \sum\limits_{j=1}^{C} q_{ij} - q_{11})
    
    Parameters
    ----------
    predicted : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
        predicted tensor
    target : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
        ground truth tensor
    num_classes : `int <https://docs.python.org/3/library/functions.html#int>`_
        number of classes

    Returns
    -------
    `float <https://docs.python.org/3/library/functions.html#float>`_
        mIoU value

    References
    ----------
    https://arxiv.org/pdf/2010.05687.pdf

    """
    logging.debug("Evaluating mIoU")
    return mIoU_and_SeK(predicted, target, num_classes)[0]


def SeK(predicted, target, num_classes):
    """Computes Separated Kappa (Sek) coefficient 

    For a confusion matrix, :math:`SeK` is computed as:

    .. math:: SeK = e^{(IOU_2 - 1)} \cdot (\hat{\\rho} - \hat{\\eta}) / (1 - \hat{\\eta}) 

    where :math:`IOU_2` evaluates extraction of changed regions, and is computed as:

    .. math:: IOU_2 = \sum\limits_{i=2}^{C} \sum\limits_{j=2}^{C} q_{ij}/(\sum\limits_{i=1}^{C} \sum\limits_{j=1}^{C} q_{ij} - q_{11})

    and :math:`\hat{\\rho}` and :math:`\hat{\\eta}` as computed as:

    .. math:: \hat{\\rho} = \sum\limits_{i=2}^{C} q_{ii} /(\sum\limits_{i=1}^{C} \sum\limits_{j=1}^{C} q_{ij} - q_{11})

    .. math:: \hat{\\eta} = \sum\limits_{j=1}^{C} ( \hat{q}_{j+} \cdot \hat{q}_{+j} ) / (\sum\limits_{i=1}^{C} \sum\limits_{j=1}^{C} q_{ij} - q_{11})^2

    where :math:`\hat{q}_{j+}` and :math:`\hat{q}_{+j}` represent row sum and column sum of confusion matrix without :math:`q_{11}`

    Parameters
    ----------
    predicted : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
        predicted tensor
    target : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
        ground truth tensor
    num_classes : `int <https://docs.python.org/3/library/functions.html#int>`_
        number of classes

    Returns
    -------
    `float <https://docs.python.org/3/library/functions.html#float>`_
        SeK value

    References
    ----------
    https://arxiv.org/pdf/2010.05687.pdf
    
    """
    logging.debug("Evaluating SeK")
    return mIoU_and_SeK(predicted, target, num_classes)[1]
