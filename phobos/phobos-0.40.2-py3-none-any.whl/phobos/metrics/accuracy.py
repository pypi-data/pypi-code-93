import torch


def Acc(y_pred, y_true, mask=None, thresh=0.5):
    """Computes accuracy metric

    Parameters
    ----------
    y_pred : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
        predicted tensor
    y_true : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
        ground truth tensor
    mask : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_, optional
        accuracy mask, by default None
    thresh : `float <https://docs.python.org/3/library/functions.html#float>`_, optional
        threshold, by default 0.5

    Examples
    --------
    >>> criterion = Acc
    >>> predicted = torch.zeros(2, 32)
    >>> target = torch.zeros(2, 32)
    >>> loss = criterion(predicted, target)
    >>> loss.item()
    1.0

    >>> mask = torch.zeros((2,32), dtype=torch.float32)
    >>> criterion = Acc
    >>> predicted = torch.zeros(2, 32)
    >>> target = torch.zeros(2, 32)
    >>> loss = criterion(predicted, target, mask)
    >>> loss.item()
    0.0

    Returns
    -------
    `float <https://docs.python.org/3/library/functions.html#float>`_
        accuracy
    """
    y_pred = (y_pred >= thresh).type(torch.float32)
    if mask is None:
        res = torch.all((y_true == y_pred), dim=-1)
        res = torch.mean(res.type(torch.float32))
        return res
    else:
        res = y_true == y_pred
        res[torch.logical_not(mask.type(torch.bool))] = True
        res = torch.all(res, dim=-1)
        mask = torch.logical_not(torch.all(torch.logical_not(mask), dim=-1))
        if mask.type(torch.float32).sum() == 0:
            return torch.tensor(0.0)
        res = torch.mean(res[mask].type(torch.float32))
        return res
