"""
Demo file for multiscale BM3D streak denoising, based on
Mäkinen, Y., Marchesini, S., Foi, A., 2021,
"Ring artifact reduction via multiscale nonlocal collaborative filtering of spatially correlated noise"
J. Synchrotron Rad. 28(3). DOI: http://doi.org/10.1107/S1600577521001910
"""

from bm3d_streak_removal import multiscale_streak_removal, normalize_data, \
    extreme_streak_attenuation, default_horizontal_bins, full_streak_pipeline
import numpy as np
from scipy.io import loadmat
import matplotlib.pyplot as plt

### Load sample data

# Load example file, which contains a slice of TomoBank sample "00076" from Argonne National Laboratory:
# De Carlo, Francesco, et al. “TomoBank: a tomographic data repository for computational x-ray science.”
# Measurement Science and Technology 29.3 (2018): 034004.
# http://www.doi.org/10.1088/1361-6501/aa9c19
#
# More info & download instructions for the full sample at the TomoBank website:
# https://tomobank.readthedocs.io/en/latest/source/data/docs.data.rings.html
# See tomobank_license.txt for license information for this data.

datafile = loadmat('tomobank_00076_exchange_slices.mat')
data = datafile['data'] # A slice of /exchange/data
brightfields = datafile['data_white'] # A slice of /exchange/data_white (corresponding to "data")
darkfields = datafile['data_dark'] # A slice of /exchange/data_dark (corresponding to "data")

# Average the ten samples to obtain a single field for both
brightfield = np.mean(np.array(brightfields, dtype=np.float32), axis=2, dtype=np.float32)
darkfield = np.mean(np.array(darkfields, dtype=np.float32), axis=2, dtype=np.float32)

# Transpose the arrays such that the first dimension is angle
data = np.transpose(data, [2, 1, 0])
brightfield = np.transpose(brightfield, [1, 0])
darkfield = np.transpose(darkfield, [1, 0])


### Process sinogram:

# (Equivalent to:)
#data_denoised = full_streak_pipeline(data, brightfield, darkfield)

# Apply normalizations
data_norm0 = normalize_data(data, brightfield, darkfield)
data_norm0 = np.log(data_norm0)

# Apply extreme streak attenuation
data_norm = extreme_streak_attenuation(data_norm0)

# Apply multiscale filtering
data_denoised = multiscale_streak_removal(data_norm)

### Adjusting the filter:

# All algorithm parameters are automatically calculated based on the input data.

# The main extra parameter is the horizontal binning count ("K"). 
# The automatic value is based solely on axis size; while the usually a good guess,
# it may be possible to improve denoising quality by adjusting it.
# To reduce the number of scales (the denoising result was oversmooth in low frequencies):

# Bin count when max_bin_iter_horizontal='auto' (default)
#default_bin_count = default_horizontal_bins(data_norm)

# Use one scale less
#data_denoised = multiscale_streak_removal(data_norm, max_bin_iter_horizontal=default_bin_count-1)

# Likewise, if the widest streaks were not denoised, try one scale more:
#data_denoised = multiscale_streak_removal(data_norm, max_bin_iter_horizontal=default_bin_count+1)

# For simple overall BM3D filtering strength adjustment, use the filter_strength parameter (default is 1):
#data_denoised = multiscale_streak_removal(data_norm, filter_strength=1.1)


# Show some resulting sinograms
plt.imshow(np.concatenate((data_norm0[:, 3, :], data_denoised[:, 3, :]), axis=1))
plt.show()


