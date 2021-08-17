#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-11-07 17:00:48
# @Author  : Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$

import torch as th
import numpy as np
import torchsar as ts


def unwrap(x, discont=3.141592653589793, axis=-1, imp='numpy'):
    r"""Unwrap by changing deltas between values to $2*\pi$ complement.

    Unwrap radian phase `x` by changing absolute jumps greater than
    `discont` to their 2*pi complement along the given axis.

    Parameters
    ----------
    x : Tensor or ndarray
        The input.
    discont : float, optional
        Maximum discontinuity between values, default is $\pi$.
    axis : int, optional
        Axis along which unwrap will operate, default is the last axis.
    imp : str, optional
        Implenmentation way, ``'numpy'`` --> numpy

    Returns
    -------
    Tensor or ndarray
        The unwrapped.
    """

    if imp in ['numpy', 'np', 'NUMPY', 'NP']:
        y = np.unwrap(x, discont=discont, axis=axis)
        if type(x) is th.Tensor:
            return th.tensor(y, dtype=x.dtype, device=x.device)
        elif type(x) is list:
            return list(y)
        else:
            return y


def unwrap2(x, discont=3.141592653589793, axis=-1, imp='numpy'):
    r"""Unwrap by changing deltas between values to $2*\pi$ complement.

    Unwrap radian phase `x` by changing absolute jumps greater than
    `discont` to their 2*pi complement along the given axis. The elements
    are divided into 2 parts (with equal length) along the given axis.
    The first part is unwrapped in inverse order, while the second part
    is unwrapped in normal order.

    Parameters
    ----------
    x : Tensor or ndarray
        The input.
    discont : float, optional
        Maximum discontinuity between values, default is $\pi$.
    axis : int, optional
        Axis along which unwrap will operate, default is the last axis.
    imp : str, optional
        Implenmentation way, ``'numpy'`` --> numpy

    Returns
    -------
    Tensor or ndarray
        The unwrapped.
    """
    s = x.shape[axis]
    i = int(s / 2)
    if imp in ['numpy', 'np', 'NUMPY', 'NP']:
        if type(x) is th.Tensor:
            xtype = 'torch.Tensor'
            xdtype, xdevice = x.dtype, x.device
            x = x.numpy()
        else:
            xtype = 'numpy.array'
        d = np.ndim(x)
        idx1 = ts.sl(d, [axis], [slice(i - 1, None, -1)])
        y1 = np.unwrap(x[idx1], discont=discont, axis=axis)
        idx2 = ts.sl(d, [axis], [slice(i, s, 1)])
        y2 = np.unwrap(x[idx2], discont=discont, axis=axis)
        y = np.concatenate((y1[idx1], y2), axis=axis)
        if xtype is 'torch.Tensor':
            return th.tensor(y, dtype=xdtype, device=xdevice)
        else:
            return y


if __name__ == '__main__':

    x_np = np.array([3.14, -3.12, 3.12, 3.13, -3.11])
    y_np = unwrap(x_np)
    print(y_np, y_np.shape, type(y_np))
    x_th = th.Tensor(x_np)
    y_th = unwrap(x_th)
    print(y_th, y_th.shape, type(y_th))

    print("------------------------")
    x_np = np.array([3.14, -3.12, 3.12, 3.13, -3.11])
    x_np = np.concatenate((x_np[::-1], x_np), axis=0)
    print(x_np)
    y_np = unwrap2(x_np)
    print(y_np, y_np.shape, type(y_np))

