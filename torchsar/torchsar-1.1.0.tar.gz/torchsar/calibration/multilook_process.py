#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-01-05 11:06:13
# @Author  : Yan Liu & Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$
from __future__ import division, print_function, absolute_import
import torch as th


def multilook_spatial(Sslc, nlooks):
    r"""spatial multilook processing

    spatial averaging in azimuth or range direction.

    Args:
        Sslc (Tensor): Processed single look complex (or intensity) sar data tensor with size :math:`N_a×N_r`.
        nlooks (tuple or list): The number of looks in azimuth and range direction, [na, nr] or (na, nr).

    Returns:
        Smlc (Tensor): Processed multi-look complex tensor.

    """

    Na, Nr = Sslc.shape
    if nlooks is None:
        return Sslc

    # spatial averaging
    if nlooks[0] > 1:
        Smlca = th.zeros((int(Na / nlooks[0]), Nr), dtype=Sslc.dtype, device=Sslc.device)
        index = 0
        for a in range(0, Na - nlooks[0], nlooks[0]):
            Smlca[index, :] = th.mean(Sslc[a:a + (nlooks[0] - 1), :], axis=0)
            index += 1
    else:
        Smlca = Sslc

    Na, Nr = Smlca.shape

    if nlooks[1] > 1:
        Smlc = th.zeros((Na, int(Nr / nlooks[1])), dtype=Sslc.dtype, device=Sslc.device)
        index = 0
        for r in range(0, Nr - nlooks[1], nlooks[1]):
            Smlc[:, index] = th.mean(Smlca[:, r:r + (nlooks[1] - 1)], axis=1)
            index += 1
    else:
        Smlc = Smlca

    return Smlc


if __name__ == '__main__':

    Na, Nr = (1025, 256)
    real = th.randn(Na, Nr)
    imag = th.randn(Na, Nr)
    print(real.shape, imag.shape)
    Sslc = real + 1j * imag
    Smlc = multilook_spatial(Sslc, nlooks=(4, 1))

    print(Smlc.shape)
