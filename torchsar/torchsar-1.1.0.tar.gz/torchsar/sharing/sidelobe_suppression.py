#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2021-03-18 11:06:13
# @Author  : Yan Liu & Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$
from __future__ import division, print_function
import torch as th
from torchsar.dsp.ffts import fft, ifft
from torchsar.sharing.window_function import window


def sls_fd(x, axis=0, wtype=None, dtype=None):
    """Sidelobe suppression in frequency domain

    Sidelobe suppression in frequency domain


    Parameters
    ----------
    x : tensor
        The input.
    axis : int, optional
        The axis for sidelobe-suppression.
    wtype : str or None, optional
        The type of window, default is None. see :func:`window`.
    dtype : torch's dtype or None, optional
        The data type. If None, use default dtype of torch.

    Returns
    -------
    tensor
        The suppressed.
    """

    n = x.size(axis)
    shape = [1] * x.dim()
    shape[axis] = n
    w = window(n, wtype=wtype, dtype=dtype).reshape(shape)
    x = fft(x, axis=axis, shift=True)
    x = x * w
    x = ifft(x, axis=axis, shift=True)

    return x
