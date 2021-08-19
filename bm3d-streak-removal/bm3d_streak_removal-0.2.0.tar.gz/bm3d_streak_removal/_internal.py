"""
Functions used in the filtering process.
"""
import numpy as np
import bm3d
from scipy.signal import convolve, convolve2d, gaussian
from scipy.interpolate import interp1d
from scipy.fftpack import fft, fft2
from typing import List, Iterable, Union

def default_horizontal_bins(data: np.ndarray) -> int:
    """
    Get number of horizontal bins based on input size
    :param data: stack of sinograms
    :return: horizontal bin count (number of scales)
    """

    dim = 2 if data.ndim == 3 else 1
    return np.maximum(0, int(np.floor(np.log2(data.shape[dim] / 40))))

def bin_and_bm3d_single(z: np.ndarray, pro: bm3d.BM3DProfile, max_bin_main: int, bin_size_second: int,
                         psd_shapes: List[np.ndarray], slice_sizes: List[int], slice_step_sizes: List[int]) \
        -> np.ndarray:
    """
    Perform multiscale BM3D denoising on a single sinogram.
    :param z: The sinogram, streaks along dimension 0
    :param pro: BM3D parameters
    :param max_bin_main: Number of scales horizontally
    :param bin_size_second: vertical binning divisor
    :param psd_shapes: adjusts the shape of the PSD for each scale
    :param slice_sizes: list of length max_bin_main corresponding to horizontal slice sizes
    :param slice_step_sizes: list of length max_bin_main corresponding to horizontal slicing step size
    :return: denoised image
    """

    # Shrink along the first dimension
    shrunk_y = _bin_in_1d(z, bin_size_second, dim=0)
    zbins_orig = [np.copy(shrunk_y)]

    # Contains upscaled denoised sinograms
    zbins = [np.zeros(0)]

    den = None

    # Bin horizontally
    for i in range(0, max_bin_main):
        zbins_orig.append(_bin_in_1d(zbins_orig[-1], 2, dim=1))
        zbins.append(np.zeros(0))

    zbins[-1] = zbins_orig[-1]

    for ii in range(max_bin_main, -1, -1):
        print("k:", ii)
        img = zbins[ii]

        # Denoise binned sinogram, if slice size is smaller than img, split before denoising and PSD est.
        den = _denoise_in_slices(img, pro, psd_shapes[ii], slice_sizes[ii], slice_step_sizes[ii])
        # For iterations except the last, create the next noisy image with a finer scale residual
        if ii > 0:
            debin = _debin_in_1d(den - zbins_orig[ii], zbins_orig[ii - 1].shape[1], 2, 30, dim=1)
            zbins[ii - 1] = zbins_orig[ii - 1] + debin

    # Vertical upscaling + residual
    den = z + _debin_in_1d(den - shrunk_y, z.shape[0], bin_size_second, 30, dim=0)

    return den


def get_psd_shapes(denoise_sizes: List[int]) -> List[np.ndarray]:
    """
    Get one-dimensional PSD shapes (normalized to norm=1) based on the sizes of input sinograms.
    Smallest size PSD is presumed to be flat; the full PSD should be of form
    psd = np.zeros(denoise_sizes[i]); psd[0, :] = psd_shapes[i] * psd_norm;
    :param denoise_sizes: List of horizontal sizes of sinograms to be denoised, either the full bin sizes or slices.
    :return: List of 1-D numpy arrays, each of which corresponds to the shape of the horizontal streak
    component of the PSD
    """
    psd_shapes = []
    # For each size except the last, calculate normalized PSD with the residual kernel
    for i in range(0, len(denoise_sizes) - 1):
        # Pre-computed residual noise kernel corresponding to the used binning functions
        residual_kernel_half = [-0.000038014, -0.00018945, -0.0005779, -0.0006854,
                                -0.00017558, -0.00078497, -0.002597, -0.0017638, 0.0014121, -0.0012586, -0.0087586,
                                -0.0045105, 0.0062736, -0.0058483, -0.021518, -0.010869, -0.060379, -0.2232, 0.68939]

        residual_kernel_half = residual_kernel_half[np.maximum(0, (len(residual_kernel_half) * 2 - 1 - denoise_sizes[i]) // 2):]

        residual_kernel = residual_kernel_half + residual_kernel_half[-2::-1]


        sz = denoise_sizes[i]
        psd = np.abs(fft(residual_kernel, sz)) ** 2
        psd_shapes.append(psd)

    # Last PSD shape is flat
    sz = denoise_sizes[-1]
    psd_shapes.append(np.ones(sz,) / np.sqrt(sz))

    return psd_shapes


def resolve_default_parameters(data: np.ndarray, max_bin_iter_horizontal: Union[int, str],
                                bin_vertical: Union[int, str],
                                filter_strength: float, use_slices: bool,
                                slice_sizes: List[int], slice_step_sizes: List[int],
                                bm3d_profile_obj: bm3d.BM3DProfile, denoise_indices: Iterable) \
        -> (int, int, List[int], List[int], bm3d.BM3DProfile, Iterable):
    """
    Resolve default parameters in case they were not provided.
    :param data: Input data
    :param max_bin_iter_horizontal: maximum number of horizontal bins
    :param bin_vertical: vertical binning size
    :param filter_strength: adjust BM3D filter strength (1 is normal strength)
    :param use_slices: True if slices should be used in denoising
    :param slice_sizes: list of slice sizes of length max_bin_iter_horizontal if use_slices=True
    :param slice_step_sizes: list of slice step sizes of length max_bin_iter_horizontal if use_slices=True
    :param bm3d_profile_obj: BM3D parameters
    :param denoise_indices: indices to be denoised, None if all
    :return: parameters, where default values have been replaced:
    max_bin_iter_horizontal, bin_vertical, denoise_sizes, slice_step_sizes, bm3d_profile_obj, denoise_indices
    """
    # Define binning counts if not provided as input

    if bin_vertical == 'auto':
        # Default vertical result size to be about 64 pixels
        bin_vertical = np.maximum(0, int(np.ceil(data.shape[0] / 64)))

    if max_bin_iter_horizontal == 'auto':
        # Default horizontal minimum to be under 40 pixels -- each binning halves size
        max_bin_iter_horizontal = np.maximum(default_horizontal_bins(data), 0)

    if not use_slices or slice_sizes is None:
        denoise_sizes = []
        for i in range(0, max_bin_iter_horizontal + 1):
            if use_slices:
                denoise_sizes.append(39)
            else:
                denoise_sizes.append(data.shape[2] // 2 ** i)
    else:
        denoise_sizes = slice_sizes

    if slice_step_sizes is None:
        slice_step_sizes = []

    for i in range(0, max_bin_iter_horizontal + 1):
        if len(slice_step_sizes) < i + 1:
            slice_step_sizes.append(denoise_sizes[i] // 2)
        if denoise_sizes[i] > data.shape[2] // 2 ** i:
            denoise_sizes[i] = (data.shape[2] // 2 ** i)

    if bm3d_profile_obj is None:
        # Pre-defined profile
        pro = bm3d.BM3DProfile()
        pro.lambda_thr3d = pro.lambda_thr3d_re = 3.5
        pro.mu2 = pro.mu2_re = 0.8
        pro.denoise_residual = True
        pro.filter_strength = filter_strength
        bm3d_profile_obj = pro

    if denoise_indices is None:
        denoise_indices = range(0, data.shape[1])

    return max_bin_iter_horizontal, bin_vertical, denoise_sizes, slice_step_sizes, bm3d_profile_obj, denoise_indices

def _generate_2d_poly_frames_and_windows(x_size: int, y_size: int) -> (dict, dict):
    """
    Generate polynomials used for local detrending
    :param x_size: maximum width
    :param y_size: maximum weight
    :return: maps of frames and weighted analysis matrices of varying sizes
    """
    frame_map = {}
    analysis_map = {}

    # Base meshgrids
    t_2_o, t_1_o = np.meshgrid(np.linspace(-1, 1, x_size), np.linspace(-1, 1, y_size))

    half_x = x_size // 2
    half_y = y_size // 2
    for sz1 in range(0, y_size):
        for sz2 in range(0, x_size):

            # Crop base meshes to account for edge positions
            t_2 = t_2_o[max(0, half_y - sz1):y_size + min(0, half_y - sz1),
                  max(0, half_x - sz2):x_size + min(0, half_x - sz2)]
            t_1 = t_1_o[max(0, half_y - sz1):y_size + min(0, half_y - sz1),
                  max(0, half_x - sz2):x_size + min(0, half_x - sz2)]

            m = []

            # Polynomial order
            n = 3
            for j in range(0, n + 1):
                for k_1 in range(0, j + 1):
                    k_2 = j - k_1
                    m.append(np.ravel(t_1) ** k_1 * np.ravel(t_2) ** k_2)

            # Weighing window; ignore both immediate neighbors and faraway values
            s = 0.2
            s2 = 0.7
            w = np.exp(-((0.5 / s2 ** 2) * t_2 ** 2 + (0.5 / s2 ** 2) * t_1 ** 2)) * np.minimum(
                1 / np.exp(-((0.5 / s ** 2) * t_2 ** 2 + (0.5 / s ** 2) * t_1 ** 2)), 10) / 10
            w[sz1 - max(sz1 - half_y, 0), sz2 - max(sz2 - half_x, 0)] = 0
            local_w = w

            m = np.array(m).T
            frame_map[(sz1, sz2)] = m

            m_tilde = m @ np.linalg.pinv((m.T * np.ravel(local_w)) @ m)
            analysis_map[(sz1, sz2)] = m_tilde.T * np.ravel(local_w)

    return frame_map, analysis_map


def median_filter_at_positions(data: np.ndarray, positions: np.ndarray, half_kern_sz: int) -> np.ndarray:
    """
    Replace predetermined columns of data with medians
    :param data: input data (3-D), streaks are along dimension 0
    :param positions: array with size (data.shape[1], data.shape[2])
                      where positions of broken pixels are 1
    :param half_kern_sz: The size for median neighborhood for replacement data is (half_kern_sz * 2) + 1
    :return: filtered data (copy, same shape as data)
    """

    median_filtered_data = np.copy(data)

    # set broken pixels to nan
    median_filtered_data[np.atleast_3d(positions).transpose((2, 0, 1)).repeat(data.shape[0], axis=0)] = np.nan

    for i in range(data.shape[1]):
        for j in range(data.shape[2]):
            if positions[i, j]:
                # Get range centered at i, j and make sure it doesn't go out of bounds
                start_i = max(i - half_kern_sz, 0)
                end_i = min(i + half_kern_sz, data.shape[1] - 1)
                start_j = max(j - half_kern_sz, 0)
                end_j = min(j + half_kern_sz, data.shape[2] - 1)

                for k in range(data.shape[0]):
                    neighborhood_data = median_filtered_data[k, start_i:end_i, start_j:end_j]
                    neighborhood_data = neighborhood_data[~np.isnan(neighborhood_data)]
                    if len(neighborhood_data) == 0:
                        neighborhood_data = data[k, i, j]
                    median_filtered_data[k, i, j] = np.median(neighborhood_data)

    return median_filtered_data


def data_simple_streak_detect_thr(data: np.ndarray, lambda_filt: float, half_kern_sz: int) -> np.ndarray:
    """
    Detect extreme streaks in the data based on local thresholds in square moving window.
    :param data: input data (3-D), streaks along dimension 0
    :param lambda_filt: threshold parameter for streak detection
    :param half_kern_sz: Kernel size for detrending & calculating std is (half_kern_sz * 2) + 1
    :return: positions of detected streaks as a 2-D array
    """

    # Consider only medians in streak direction to detect streaks
    inp = np.median(data, axis=0)
    data_sz = inp.shape
    data_med_detect = np.zeros(data_sz)
    data_local_var = np.zeros(data_sz)

    y_sz = np.minimum(half_kern_sz, (data_sz[0]-1)//2)

    # Generate polynomials to do local detrending for std
    frame_map, analysis_map = _generate_2d_poly_frames_and_windows(half_kern_sz * 2 + 1,
                                                                   y_sz * 2 + 1)

    for i in range(data_sz[0]):
        for j in range(data_sz[1]):
            # Get range centered at i, j and make sure it doesn't go out of bounds
            start_i = max(i - y_sz, 0)
            end_i = min(i + y_sz + 1, data_sz[0])
            start_j = max(j - half_kern_sz, 0)
            end_j = min(j + half_kern_sz + 1, data_sz[1])

            neighborhood_data = np.copy(inp[start_i:end_i, start_j:end_j])

            coord_y = i if i < y_sz else \
                y_sz * 2 + 1 - (data_sz[0] - i) if i >= data_sz[0] - y_sz else y_sz
            coord_x = j if j < half_kern_sz else \
                half_kern_sz * 2 + 1 - (data_sz[1] - j) if j >= data_sz[1] - half_kern_sz else half_kern_sz

            # Local detrend
            m = frame_map[coord_y, coord_x]

            fit_neighborhood = m @ (analysis_map[coord_y, coord_x] @ np.ravel(neighborhood_data))

            neighborhood_data -= fit_neighborhood.reshape([end_i - start_i, end_j - start_j])

            current_datapoint = neighborhood_data[(i - start_i), (j - start_j)]

            data_med_detect[i, j] = np.abs(current_datapoint)
            data_local_var[i, j] = np.var(neighborhood_data)

    return data_med_detect > lambda_filt * np.sqrt(data_local_var)



def _estimate_std(z: np.ndarray, psd_unscaled: np.ndarray) -> float:
    """
    Estimate noise std, presuming noise is approx. constant vertical streaks (along dimension 0)
    :param z: Sinogram to estimate the std
    :param psd_unscaled: complete PSD shape, apart from scaling
    :return: MAD estimate of std
    """
    db3 = [-0.33267055295008, 0.80689150931109, -0.45987750211849,
           -0.13501102001025, 0.08544127388203, 0.03522629188571]
    gau = gaussian(z.shape[0] // 2, std=z.shape[0] / 12)
    g_d = (np.array(db3, ndmin=2).T * gau).T
    h = convolve(z, g_d, 'valid')

    mad_scaling = np.sqrt(z.size) / np.linalg.norm((np.sqrt(psd_unscaled) * np.abs(fft2(g_d, shape=z.shape))).ravel())
    mad = np.median(abs(h-np.median(h))) / 0.674489750196082

    return mad * mad_scaling


def _create_arr_for_bin(base_arr: np.ndarray, h: int, dim: int):
    """
    Create a padded and convolved array used in both binning and debinning.
    :param base_arr: Input array
    :param h: bin count
    :param dim: bin dimension (0 or 1)
    :return: resulting array
    """
    mod_pad = h - ((base_arr.shape[dim] - 1) % h) - 1
    if dim == 0:
        pads = ((0, mod_pad), (0, 0))
        kernel = np.ones((h, 1))
    else:
        pads = ((0, 0), (0, mod_pad))
        kernel = np.ones((1, h))

    return convolve2d(np.pad(base_arr, pads, 'symmetric'), kernel, 'same', 'fill')


def _bin_in_1d(z: np.ndarray, h: int = 2, dim: int = 1) -> np.ndarray:
    """
    Bin a 2-D array across a dimension
    :param z: input data (2-D)
    :param h: divisor for binning
    :param dim: dimension for binning (0 or 1)
    :return: binned data
    """

    if h > 1:
        h_half = h // 2
        z_bin = _create_arr_for_bin(z, h, dim)

        # get coordinates of bin centres
        if dim == 0:
            z_bin = z_bin[h_half + ((h % 2) == 1): z_bin.shape[dim] - h_half + 1: h, :]
        else:
            z_bin = z_bin[:, h_half + ((h % 2) == 1): z_bin.shape[dim] - h_half + 1: h]

        return z_bin

    return z


def _debin_in_1d(z: np.ndarray, size: int, h: int, n_iter: int, dim: int = 1) -> np.ndarray:
    """
    De-bin a 2-D array across a dimension
    :param z: input data (2-D)
    :param size: target size (original size before binning) for the second dimension
    :param h: binning factor (original divisor)
    :param n_iter: number of iterations
    :param dim: dimension for binning (0 or 1)
    :return: debinned image, size of "size" across bin dimension
    """
    if h <= 1:
        return np.copy(z)

    h_half = h // 2

    if dim == 0:
        base_arr = np.ones((size, 1))
    else:
        base_arr = np.ones((1, size))

    n_counter = _create_arr_for_bin(base_arr, h, dim)

    # coordinates of bin counts
    x1c = np.arange(h_half + ((h % 2) == 1), (z.shape[dim]) * h, h)
    x1 = np.arange(h_half + 1 - ((h % 2) == 0) / 2, (z.shape[dim]) * h, h)

    # coordinates of image pixels
    ix1 = np.arange(1, size + 1)

    y_j = 0

    for jj in range(max(1, n_iter)):
        # residual
        if jj > 0:
            r_j = z - _bin_in_1d(y_j, h, dim)
        else:
            r_j = z

        # interpolation
        if dim == 0:
            interp = interp1d(x1, r_j / n_counter[x1c, :], kind='cubic', fill_value='extrapolate', axis=0)
        else:
            interp = interp1d(x1, r_j / n_counter[:, x1c], kind='cubic', fill_value='extrapolate')
        y_j = y_j + interp(ix1)

    return y_j


def _estimate_psd_and_denoise(z: np.ndarray, psd_shape: np.ndarray, pro: bm3d.BM3DProfile) \
        -> np.ndarray:
    """
    Perform PSD estimation and BM3D denoising for a single scale sinogram or slice.
    :param z: Noisy input (2-D)
    :param psd_shape: PSD shape function of size (z.shape[1],)
    :param pro: BM3D parameters
    :return: denoised z
    """

    psd_small = np.zeros(z.shape)
    psd_small[0, :] = psd_shape
    sigma = _estimate_std(z, psd_small)
    psd_small[0, :] *= sigma ** 2 * psd_small.size
    den = bm3d.bm3d(z, psd_small, pro)

    return den


def _denoise_in_slices(zs: np.ndarray, pro: bm3d.BM3DProfile,
                       psd_shape: np.ndarray, slice_size: int, slice_step: int) -> np.ndarray:
    """
    Denoise the sinogram with BM3D, estimating the PSD from the residual.
    If slice_size < zs.shape[1], split to splices before denoising.
    :param zs: a single sinogram input (streaks along dimension 0)
    :param pro: BM3D profile
    :param psd_shape: adjusted PSD shape (size (slice_size, ))
    :param slice_size: size of a single slice to be denoised
    :param slice_step: step of moving slice window
    :return: denoised zs
    """

    # Do at once
    if slice_size >= zs.shape[1]:
        den = _estimate_psd_and_denoise(zs, psd_shape, pro)
        return den

    # Split up
    den = np.zeros(zs.shape)
    buff = np.zeros((1, zs.shape[1]))

    # Window function for slice aggregation
    t = np.linspace(-1, 1, slice_size)
    s = 0.01
    w = np.exp((-0.5 / (slice_size * s) ** 2) * t ** 2)
    for p in range(0, zs.shape[1] - slice_size + slice_step, slice_step):
        st_ix = zs.shape[1] - slice_size if p + slice_size > zs.shape[1] else p
        end_ix = st_ix + slice_size

        zs_slice = zs[:, st_ix:end_ix]
        den[:, st_ix:end_ix] += w * _estimate_psd_and_denoise(zs_slice, psd_shape, pro)
        buff[0, st_ix:end_ix] += w

    return den / buff