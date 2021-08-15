# normalize map in Fourier space for rcc calculation
import numpy as np
import scipy.signal
from emda.core import restools


def get_normalized_fo(fo, kern):
    # calculate local density variance
    loc_A = scipy.signal.fftconvolve(fo, kern, "same")
    loc_A2 = scipy.signal.fftconvolve(fo * np.conjugate(fo), kern, "same")
    var_A = loc_A2 - loc_A * np.conjugate(loc_A)
    # masking
    var_A_tmp = np.where(var_A.real <= 0.0, 1.e-3, var_A.real)
    # normalize fo
    temp = (fo / np.sqrt(var_A_tmp))
    normalized_filtered_fo = np.where(var_A.real <= 0.0, 0.0, temp)    
    return normalized_filtered_fo


def get_fcc(f1, f2, kern):
    from emda.ext.fouriersp_local import get_3d_fouriercorrelation

    half_cc, full_cc, true_cc = get_3d_fouriercorrelation(hf1=f1, hf2=f2, kern_sphere=kern)
    return half_cc.real, full_cc.real, true_cc.real


def rcc_from_edata(f_hf1, f_hf2, kern_size=5, mapmodelrcc=False):
    from emda.ext.realsp_local import get_3d_realspcorrelation

    kern = restools.create_soft_edged_kernel_pxl(kern_size)
    norm_f_hf1 = get_normalized_fo(fo=f_hf1, kern=kern)
    norm_f_hf2 = get_normalized_fo(fo=f_hf2, kern=kern)
    if mapmodelrcc:
        fcc_true = get_fcc(f1=f_hf1, f2=f_hf2, kern=kern)[0]
    else:
        fcc_true = get_fcc(f1=f_hf1, f2=f_hf2, kern=kern)[2]
    norm_map1 = (np.fft.ifftn(norm_f_hf1 * fcc_true)).real
    norm_map2 = (np.fft.ifftn(norm_f_hf2 * fcc_true)).real
    halfmapscc = get_3d_realspcorrelation(half1=norm_map1, half2=norm_map2, kern=kern)
    return halfmapscc