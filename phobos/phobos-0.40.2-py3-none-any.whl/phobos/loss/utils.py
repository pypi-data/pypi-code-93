import logging
import torch.nn as nn

from .dice import DiceLoss
from .dice_spline import DiceSplineLoss
from .focal import FocalLoss
from .jaccard import JaccardLoss
from .binary_jaccard import BCEJaccardLoss
from .spline import SplineLoss
from .tversky import TverskyLoss
from .mse import MSELoss
from .mae import MAELoss
from .nll import NLL_Loss
from .ml_dice import MLDiceLoss

loss_map_args = {
    'dice': DiceLoss,
    'ml_dice': MLDiceLoss,
    'focal': FocalLoss,
    'jaccard': JaccardLoss,
    'tversky': TverskyLoss,
    'spline': SplineLoss,
    'dice_spline': DiceSplineLoss,
    'binary_jaccard': BCEJaccardLoss,
    'mse': MSELoss,
    'mae': MAELoss,
    'nll': NLL_Loss
}

loss_map_noargs = {
    'ce': nn.CrossEntropyLoss,
    'mlsml': nn.MultiLabelSoftMarginLoss,
    'mlbce': nn.BCEWithLogitsLoss
}


def get_loss(loss_str, loss_args=None):
    """Get loss function based on passed args.

    Parameters
    ----------
    loss_str : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        string representing loss.
    loss_args : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        dictionary of loss parameters

    Examples
    --------
    >>> params = {
    ...        'loss': 'focal',
    ...        'loss_args': {
    ...            'gamma': 2,
    ...            'alpha': 1
    ...        }
    ...   }
    >>> args = Namespace(**params)
    >>> criterion = get_loss(loss_str=args.loss, loss_args=args.loss_args)
    >>> predicted = torch.zeros(2, 2, 32, 32)
    >>> target = torch.zeros(2, 32, 32)
    >>> loss = criterion(predicted, target)
    >>> loss.item()
    0.0

    >>> loss_str = 'tversky'
    >>> loss_args = {
        ...    'beta': 0.5,
        ...    'alpha': 0.5
        ...    }
    >>> criterion = get_loss(loss_str, loss_args)
    >>> predicted = torch.ones(2, 1, 32, 32)
    >>> target = torch.zeros(2, 32, 32)
    >>> loss = criterion(predicted, target)
    >>> loss.item()    
    1.0

    Returns
    -------
    `phobos.loss <https://phobos.granular.ai/phobos.loss.html>`_
        Selected loss class object.

    """
    logging.debug("Enter get_loss routine")
    if loss_str in loss_map_args:
        loss = loss_map_args[loss_str]
        return loss(**loss_args)

    if loss_str in loss_map_noargs:
        loss = loss_map_noargs[loss_str]
        return loss()


def set_loss(loss_str, loss, noargs=False):
    """Allows: 

    * Addition of a new loss to loss map
    
    * Modification of existing loss definitions in loss map

    Parameters
    ----------
    loss_str : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        string representing loss
    loss : `phobos.loss <https://phobos.granular.ai/phobos.loss.html>`_
        loss class
    noargs : `boolean <https://docs.python.org/3/library/functions.html#bool>`_
        flag representing whether loss object accepts any arguments

    Examples
    --------
    1. Add a dummy entry to loss map for a criterion requiring arguments:

    >>> class DummyLossArgs(DiceLoss):
    ...    def __init__(self, args):
    ...        super().__init__(**args)    
    >>> loss_str = 'dummy_loss_args'
    >>> set_loss(loss_str, DummyLossArgs)

    retrieve criterion using this entry during training:

    >>> loss_args = {`eps`: 0.2 }
    >>> criterion = get_loss(loss_str, loss_args=loss_args)

    use criterion to compute losses:

    >>> predicted = torch.ones(2, 1, 32, 32)
    >>> target = torch.zeros(2, 32, 32)
    >>> loss = criterion(predicted, target)

    2. Add a dummy entry to loss map for a criterion requiring no arguments:

    >>> class DummyLossNoArgs(NLL_Loss):
    ...    def __init__(self, args):
    ...        super().__init__(**args)    
    >>> loss_str = 'dummy_loss_args'
    >>> set_loss(loss_str, DummyLossArgs)

    retrieve criterion using this entry during training:

    >>> criterion = get_loss(loss_str, loss_args=None)

    use criterion to compute losses:

    >>> predicted = torch.ones(2, 1, 32, 32)
    >>> target = torch.zeros(2, 32, 32)
    >>> loss = criterion(predicted, target)
    """
    logging.debug("Enter set_loss routine")
    if noargs:
        loss_map_noargs[loss_str] = loss
    else:
        loss_map_args[loss_str] = loss
    logging.debug("Exit set_loss routine")
