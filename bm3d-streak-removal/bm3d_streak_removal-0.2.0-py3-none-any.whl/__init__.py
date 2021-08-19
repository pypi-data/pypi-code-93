"""
Streak denoising through multiscale collaborative filtering of correlated noise.
Based on Mäkinen, Y., Marchesini, S., Foi, A., 2021,
"Ring artifact reduction via multiscale nonlocal collaborative filtering of spatially correlated noise"
J. Synchrotron Rad. 28(3). DOI: http://doi.org/10.1107/S1600577521001910

## USAGE:

The denoising is applied to *sinogram data*.
*NOTE*: Input data streaks should be along the first axis:
(theta, y, x)
or
(theta, x)

For the full pipeline as described in the paper:
```
data_denoised = full_streak_pipeline(data, brightfield, darkfield)
```

For extreme streak attenuation and multiscale denoising without normalizations
(input is presumed to be in log-scale):
```
data_norm = extreme_streak_attenuation(data_norm)
data_denoised = multiscale_streak_removal(data_norm)
```

### ADJUSTING THE FILTER:

All algorithm parameters are automatically calculated based on the input data.

The main extra parameter is the horizontal binning count ("K").
The automatic value is based solely on axis size; while the usually a good guess,
it may be possible to improve denoising quality by adjusting it.
To reduce the number of scales (the denoising result was oversmooth in low frequencies):
```
# Bin count when max_bin_iter_horizontal='auto' (default)
default_bin_count = default_horizontal_bins(data_norm)

# Use one scale less
data_denoised = multiscale_streak_removal(data_norm, max_bin_iter_horizontal=default_bin_count-1)
```
Likewise, if the widest streaks were not denoised:
```
# Use one scale more
data_denoised = multiscale_streak_removal(data_norm, max_bin_iter_horizontal=default_bin_count+1)
```

For simple overall BM3D filtering strength adjustment, use the filter_strength parameter (default is 1):
```
# Increase filtering strength slightly
data_denoised = multiscale_streak_removal(data_norm, filter_strength=1.1)
```

For other parameters, see the function definitions below.

Copyright (c) 2020-2021 Tampere University.
All rights reserved.
This work (software, material, and documentation) shall only
be used for nonprofit noncommercial purposes.
Any unauthorized use of this work for commercial or for-profit purposes
is prohibited.
"""

import numpy as np
import bm3d
from typing import Union

from ._internal import bin_and_bm3d_single as _bin_and_bm3d_single
from ._internal import data_simple_streak_detect_thr as _data_simple_streak_detect_thr
from ._internal import median_filter_at_positions as _median_filter_at_positions
from ._internal import get_psd_shapes as _get_psd_shapes
from ._internal import resolve_default_parameters as _resolve_default_parameters
from ._internal import default_horizontal_bins

def full_streak_pipeline(raw_data: np.ndarray, brightfield: np.ndarray, darkfield: np.ndarray,
                          max_bin_iter_horizontal: Union[int, str] = 'auto',
                          bin_vertical: Union[int, str] = 'auto', filter_strength: float = 1.0):
    """
    Perform full pipeline starting from bright-field normalization and returning a denoised stack.
    If the normalizations are not needed (starting from log-normalized), call instead:

    data = extreme_streak_attenuation(data)
    data_denoised = multiscale_streak_removal(data)

    :param raw_data: 3-D stack of sinograms, (angle, y, x)
    :param brightfield: A single bright-field
    :param darkfield: A single dark-field
    :param max_bin_iter_horizontal: "K" value, default is default_horizontal_bins(raw_data)
    :param bin_vertical: vertical bin size, default is int(np.ceil(raw_data.shape[0] / 64))
    :param filter_strength: Overall BM3D filtering strength, default is 1
    :return: filtered stack
    """

    # Apply normalizations
    data_norm0 = normalize_data(raw_data, brightfield, darkfield)
    data_norm0 = np.log(data_norm0)

    # Apply extreme streak attenuation
    data_norm = extreme_streak_attenuation(data_norm0)

    # Apply multiscale filtering
    return multiscale_streak_removal(data_norm, max_bin_iter_horizontal, bin_vertical, filter_strength)


def multiscale_streak_removal(data: np.ndarray, max_bin_iter_horizontal: Union[int, str] = 'auto',
                   bin_vertical: Union[int, str] = 'auto',
                   filter_strength: float = 1.0,
                   use_slices: bool = True, slice_sizes: list = None, slice_step_sizes: list = None,
                   bm3d_profile_obj: bm3d.BM3DProfile = None, denoise_indices: list = None) -> np.ndarray:
    """
    Remove sinogram (after log transform) streak noise using multi-scale BM3D-based denoising procedure.

    :param data: 3-D or 2-D array of noisy data; the first dimension should be the streak length dimension (=angle).
                 Sinograms are indexed through the second dimension such as a single sinogram is of shape
                 (N, 1, M). A 2-D input is reshaped to fit this.
    :param max_bin_iter_horizontal:
                The number of total horizontal scales (counting the full scale). Each iteration halves the size;
                ideally in the lowest-scale sinogram the widest visible streaks of the full-size sinogram
                would be around 1-2 pixels in width.
    :param bin_vertical:
                The factor of vertical binning, e.g. bin_vertical=32 would perform denoising in 1/32th of the original
                vertical size. The default value is calculated such that the height will be 64 pixels (or less).
    :param filter_strength:
                Strength of BM4D denoising (>0), where 1 is the standard application, >1 is stronger, and <1 is weaker.
                If "bm3d_profile_obj" has been specified, this value is ignored (as it already specifies this value)
    :param use_slices:
                If True, the sinograms will be split horizontally across each binning iteration into overlapping,
                full-height patches such that each will have its own separate PSD estimation. If the streak intensity
                varies depending on the horizontal position, it is best to enable this, otherwise it may slightly reduce
                denoising performance.
    :param slice_sizes:
                A list of horizontal sizes for use of the slicing if use_slices=True;
                one size for each binning iteration. By default, slice size is either 39 pixels or 1/5th of the
                total width of the current iteration, whichever is larger.
    :param slice_step_sizes:
                List of number of pixels between slices obtained with use_slices=True, one for each binning iteration.
                By default 1/4th of the corresponding slice size.
    :param bm3d_profile_obj:
                BM3DProfile object for BM3D. Default is 'refilter' with adjusted PSD scaling.
    :param denoise_indices:
                Indices of sinograms to denoise; by default, denoises the full stack provided.
                (i.e. range(data.shape[1]))
    :return: array of denoised sinograms the same shape as data
    """

    denoi_input = data
    if data.ndim == 2:
        denoi_input = np.atleast_3d(data).transpose((0, 2, 1))

    # Calculate default parameters for those which have not been supplied others
    max_bin_iter_horizontal, bin_vertical, denoise_sizes, slice_step_sizes, pro, denoise_indices = \
        _resolve_default_parameters(denoi_input, max_bin_iter_horizontal, bin_vertical, filter_strength, use_slices,
                                    slice_sizes, slice_step_sizes, bm3d_profile_obj, denoise_indices)

    # Create normalized 1-D PSD shapes for each binning iteration
    psd_shapes = _get_psd_shapes(denoise_sizes)

    # Multiscale BM3D separately for each sinogram
    denoi = np.zeros(denoi_input.shape)
    for i in denoise_indices:
        print("Denoising sinogram", i)
        img = denoi_input[:, i, :]
        denoi[:, i, :] = _bin_and_bm3d_single(img, pro, max_bin_iter_horizontal, bin_vertical,
                                              psd_shapes, denoise_sizes, slice_step_sizes)

    if data.ndim == 2:
        denoi = denoi.squeeze()

    return denoi

def normalize_data(data0: np.ndarray, brightfield: np.ndarray, darkfield: np.ndarray):
    """
    Perform bright-field normalizations
    :param data0: raw sinogram data
    :param brightfield: a single bright-field
    :param darkfield: a single dark-field
    :return: bright-field normalized sinogtams
    """

    if brightfield.ndim == 2:
        brightfield = np.array([brightfield])
    if darkfield.ndim == 2:
        darkfield = np.array([darkfield])

    # subtract background
    brightfield -= darkfield
    brightfield = np.clip(brightfield, 0, np.inf)

    # compute the mean of the brightfield in the center:
    imgshape = np.array([brightfield.shape[1], brightfield.shape[2]])
    cropshape = np.int32(imgshape / 4)
    meanbright = np.mean(brightfield[:, cropshape[0]:-cropshape[0], cropshape[1]:-cropshape[1]])

    data_normalized_1 = np.clip((data0 - darkfield) / (brightfield + meanbright * 0.001), np.finfo(np.float32).eps,
                                np.finfo(np.float32).max)

    return data_normalized_1


def extreme_streak_attenuation(data: np.ndarray, extreme_streak_iterations: int = 3, extreme_detect_lambda: float = 4,
                               extreme_detect_size: int = 9, extreme_replace_size: int = 2):
    """
    Perform "extreme streak attenuation" (detection + median filter)
    on a 3-D stack of projections. First dimension should be angle.
    :param data: bright-field normalized, log-scale data
    :param extreme_streak_iterations: number of iterations for the filter
    :param extreme_detect_lambda: consider streaks which are stronger than lambda * local std
    :param extreme_detect_size: half window size for extreme streak detection -- total (2*s + 1)
    :param extreme_replace_size: half window size for extreme streak replacement -- total (2*s + 1)
    :return: filtered input
    """

    denoi_input = data
    if data.ndim == 2:
        denoi_input = np.atleast_3d(data).transpose((0, 2, 1))

    # Perform extreme streak removal if extreme_streak_iterations > 0
    for i in range(0, extreme_streak_iterations):
        print("Median filtering, iteration", i)
        streak_locations = _data_simple_streak_detect_thr(denoi_input, extreme_detect_lambda, extreme_detect_size)
        denoi_input = _median_filter_at_positions(denoi_input, streak_locations, extreme_replace_size)

    return denoi_input


def filtered_log(data0: np.ndarray, extreme_streak_iterations: int = 3, extreme_detect_lambda: float = 4,
                 extreme_detect_size: int = 9, extreme_replace_size: int = 2):
    """
    Apply logarithm and perform "extreme streak attenuation" (detection + median filter)
    on a 3-D stack of projections. First dimension should be angle.
    :param data0: bright-field normalized, log-scale data
    :param extreme_streak_iterations: number of iterations for the filter
    :param extreme_detect_lambda: consider streaks which are stronger than lambda * local std
    :param extreme_detect_size: half window size for extreme streak detection -- total (2*s + 1)
    :param extreme_replace_size: half window size for extreme streak replacement -- total (2*s + 1)
    :return: filtered input
    """
    # Attempt to remove the strongest streaks
    data_filtered = np.log(data0)
    data_filtered = extreme_streak_attenuation(data_filtered, extreme_streak_iterations, extreme_detect_lambda,
                                               extreme_detect_size, extreme_replace_size)
    return data_filtered