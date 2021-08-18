#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel wrapper class for NGHXRG - Teledyne HxRG Noise Generator model."""

import logging
import typing as t
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from scipy import signal

from pyxel.detectors import CMOS, CMOSGeometry
from pyxel.models.charge_measurement.nghxrg.nghxrg_beta import HXRGNoise


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
def nghxrg(
    detector: CMOS,
    noise: list,
    pca0_file: t.Optional[str] = None,
    window_position: t.Optional[t.Sequence[int]] = None,
    window_size: t.Optional[t.Sequence[int]] = None,
    plot_psd: t.Optional[bool] = True,
) -> None:
    """TBW.

    :param detector: Pyxel Detector object
    :param noise:
    :param pca0_file:
    :param window_position: [x0 (columns), y0 (rows)]
    :param window_size: [x (columns), y (rows)]
    :param plot_psd:
    """
    logging.getLogger("nghxrg").setLevel(logging.WARNING)
    logging.info("")
    geo = detector.geometry  # type: CMOSGeometry
    step = 1
    if detector.is_dynamic:
        step = int(detector.time / detector.time_step)
    if window_position is None:
        window_position = [0, 0]
    if window_size is None:
        window_size = [geo.col, geo.row]
    if window_position == [0, 0] and window_size == [geo.col, geo.row]:
        window_mode = "FULL"
    else:
        window_mode = "WINDOW"

    ng = HXRGNoise(
        n_out=geo.n_output,
        time_step=step,
        nroh=geo.n_row_overhead,
        nfoh=geo.n_frame_overhead,
        reverse_scan_direction=geo.reverse_scan_direction,
        reference_pixel_border_width=geo.reference_pixel_border_width,
        pca0_file=pca0_file,
        det_size_x=geo.col,
        det_size_y=geo.row,
        wind_mode=window_mode,
        wind_x_size=window_size[0],
        wind_y_size=window_size[1],
        wind_x0=window_position[0],
        wind_y0=window_position[1],
        verbose=True,
    )  # type: HXRGNoise

    for item in noise:
        result = None  # type: t.Optional[np.ndarray]
        if "ktc_bias_noise" in item:
            # NOTE: there is no kTc or Bias noise added for first/single frame
            noise_name = "ktc_bias_noise"
            if item["ktc_bias_noise"]:
                result = ng.add_ktc_bias_noise(
                    ktc_noise=item["ktc_noise"],
                    bias_offset=item["bias_offset"],
                    bias_amp=item["bias_amp"],
                )
        elif "white_read_noise" in item:
            noise_name = "white_read_noise"
            if item["white_read_noise"]:
                result = ng.add_white_read_noise(
                    rd_noise=item["rd_noise"],
                    reference_pixel_noise_ratio=item["ref_pixel_noise_ratio"],
                )
        elif "corr_pink_noise" in item:
            noise_name = "corr_pink_noise"
            if item["corr_pink_noise"]:
                result = ng.add_corr_pink_noise(c_pink=item["c_pink"])
        elif "uncorr_pink_noise" in item:
            noise_name = "uncorr_pink_noise"
            if item["uncorr_pink_noise"]:
                result = ng.add_uncorr_pink_noise(u_pink=item["u_pink"])
        elif "acn_noise" in item:
            noise_name = "acn_noise"
            if item["acn_noise"]:
                result = ng.add_acn_noise(acn=item["acn"])
        elif "pca_zero_noise" in item:
            noise_name = "pca_zero_noise"
            if item["pca_zero_noise"]:
                result = ng.add_pca_zero_noise(pca0_amp=item["pca0_amp"])
        else:
            noise_name = ""

        if result is None:
            raise NotImplementedError

        try:
            result = ng.format_result(result)
            if result.any():
                if plot_psd:
                    display_noisepsd(
                        result,
                        noise_name=noise_name,
                        nb_output=geo.n_output,
                        dimensions=(geo.col, geo.row),
                        path=detector.output_dir,
                        step=step,
                    )
                if window_mode == "FULL":
                    detector.pixel.array += result
                elif window_mode == "WINDOW":
                    start_y_idx = window_position[1]
                    end_y_idx = window_position[1] + window_size[1]

                    start_x_idx = window_position[0]
                    end_x_idx = window_position[0] + window_size[0]

                    detector.pixel.array[
                        start_y_idx:end_y_idx, start_x_idx:end_x_idx
                    ] += result
        except TypeError:
            pass


# TODO: This generates plot. It should be in class `Output`
def display_noisepsd(
    array: np.ndarray,
    nb_output: int,
    dimensions: t.Tuple[int, int],
    noise_name: str,
    path: Path,
    step: int,
    mode: str = "plot",
) -> t.Tuple[t.Any, np.ndarray]:
    """Display noise PSD from the generated FITS file."""
    # Conversion gain
    conversion_gain = 1
    data_corr = array * conversion_gain

    """
    For power spectra, need to be careful of readout directions

    For the periodogram, using Welch's method to smooth the PSD
    > Divide data in N segment of length nperseg which overlaps at nperseg/2
    (noverlap argument)
    nperseg high means less averaging for the PSD but more points
    """
    if nb_output <= 1:
        raise ValueError("Parameter 'nb_output' must be >= 1.")

    # Should be in the simulated data header
    dimension = dimensions[0]  # type: int
    pix_p_output = dimension ** 2 / nb_output  # Number of pixels per output
    nbcols_p_channel = dimension / nb_output  # Number of columns per channel
    nperseg = int(pix_p_output / 10.0)  # Length of segments for Welch's method
    read_freq = 100000  # Frame rate [Hz]

    # Initializing table of nb_outputs periodogram +1 for dimensions
    pxx_outputs = np.zeros((nb_output, int(nperseg / 2) + 1))

    # For each output
    for i in np.arange(nb_output):
        # If i odd, flatten data since its the good reading direction
        if i % 2 == 0:
            start_x_idx = int(i * nbcols_p_channel)
            end_x_idx = int((i + 1) * nbcols_p_channel)

            output_data = data_corr[:, start_x_idx:end_x_idx].flatten()
        # Else, flip it left/right and then flatten it
        else:
            start_x_idx = int(i * nbcols_p_channel)
            end_x_idx = int((i + 1) * nbcols_p_channel)

            output_data = np.fliplr(data_corr[:, start_x_idx:end_x_idx])
            output_data.flatten()
        # output data without flipping
        # output_data = data_corr[:,int(i*(nbcols_p_channel)):
        #                         int((i+1)*(nbcols_p_channel))].flatten()

        # print(output_data, read_freq, nperseg)
        # Add periodogram to the previously initialized array
        f_vect, pxx_outputs[i] = signal.welch(output_data, read_freq, nperseg=nperseg)

    # For the detector
    # detector_data = data_corr.flatten()
    # Add periodogram to the previously initialized array
    # test, Pxx_detector = signal.welch(detector_data,
    #                                   read_freq,
    #                                   nperseg=nperseg)

    if mode == "plot":
        fig, ax1 = plt.subplots(1, 1, figsize=(8, 8))
        fig.canvas.set_window_title("Power Spectral Density")
        fig.suptitle(
            noise_name
            + " Power Spectral Density\n"
            + "Welch seg. length / Nb pixel output: "
            + str("{:1.2f}".format(nperseg / pix_p_output))
        )
        ax1.plot(f_vect, np.mean(pxx_outputs, axis=0), ".-", ms=3, alpha=0.5, zorder=32)
        for _, ax in enumerate([ax1]):
            ax.set_xlim([1, 1e5])
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_xlabel("Frequency [Hz]")
            ax.set_ylabel("PSD [e-${}^2$/Hz]")
            ax.grid(True, alpha=0.4)

        filename = path.joinpath(
            "nghxrg_" + noise_name + "_" + str(step) + ".png"
        )  # type: Path
        plt.savefig(filename, dpi=300)
        plt.close()

    result = np.asarray(np.mean(pxx_outputs, axis=0))  # type: np.ndarray
    return f_vect, result
