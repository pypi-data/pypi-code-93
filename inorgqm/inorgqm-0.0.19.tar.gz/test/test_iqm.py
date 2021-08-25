#! /usr/bin/env python3

import inorgqm.multi_electron as me
import numpy as np
import numpy.linalg as la

if __name__ == "__main__":

    k_max = 6
    j = 7.5

    jx, jy, jz, jp, jm, j2 = me.calc_ang_mom_ops(j)

    okq = me.calc_stev_ops(k_max, j, jp, jm, jz)

    CFPs = np.loadtxt('params.dat')

    HCF, cf_val, cf_vec = me.calc_HCF(j, CFPs, okq[1::2, :, :, :], k_max=6)

    jz_expect = np.diag(np.real(la.inv(cf_vec) @ jz @ cf_vec))

    fig, axes = me.barrier_figure(j, cf_val, jz_expect, show=True, yax2=True)
