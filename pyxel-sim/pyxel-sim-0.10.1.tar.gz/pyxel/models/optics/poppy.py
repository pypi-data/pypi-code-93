#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""POPPY (Physical Optics Propagation in Python) model wrapper.

It calculates the optical Point Spread Function of an optical system and applies the convolution.

Documentation:
https://poppy-optics.readthedocs.io/en/stable/index.html

See details about POPPY Optical Element classes:
https://poppy-optics.readthedocs.io/en/stable/available_optics.html

Supported optical elements:

- ``CircularAperture``
- ``SquareAperture``
- ``RectangularAperture``
- ``HexagonAperture``
- ``MultiHexagonalAperture``
- ``ThinLens``
- ``SecondaryObscuration``
- ``ZernikeWFE``
- ``SineWaveWFE``

.. code-block:: yaml

  # YAML config: arguments of POPPY optical_system
  optical_system:
  - item: CircularAperture
    radius: 1.5
  - item: ThinLens
    radius: 1.2
    nwaves: 1
  - item: ZernikeWFE
    radius: 0.8
    coefficients: [0.1e-6, 3.e-6, -3.e-6, 1.e-6, -7.e-7, 0.4e-6, -2.e-6]
    aperture_stop: false
"""

import logging
import typing as t

import matplotlib.pyplot as plt
import numpy as np
from astropy.convolution import convolve_fft
from astropy.io import fits

from pyxel.data_structure import Photon
from pyxel.detectors import Detector

try:
    import poppy as op

    WITH_POPPY: bool = True
except ImportError:
    WITH_POPPY = False


def calc_psf(
    wavelength: float,
    fov_arcsec: float,
    pixelscale: float,
    optical_system: list,
    display: bool = False,
) -> t.Tuple[t.List[fits.hdu.image.PrimaryHDU], t.List["op.Wavefront"]]:
    """Calculate the point spread function for the given optical system and optionally display the psf.

    Parameters
    ----------
    wavelength: float
        Wavelength of incoming light in meters.
    fov_arcsec: float, optional
        Field Of View on detector plane in arcsec.
    pixelscale: float
        Pixel scale on detector plane (arcsec/pixel).
        Defines sampling resolution of PSF.
    optical_system:
        List of optical elements before detector with their specific arguments.

    Returns
    -------
    psf: tuple
        Tuple of lists containing the psf and intermediate wavefronts.
    """
    if not WITH_POPPY:
        raise ImportError(
            "Missing optional package 'poppy'.\n"
            "Please install it with 'pip install pyxel-sim[model]' "
            "or 'pip install pyxel-sim[all]'"
        )

    osys = op.OpticalSystem(npix=1000)  # default: 1024

    for item in optical_system:
        if item["item"] == "CircularAperture":
            optical_item = op.CircularAperture(radius=item["radius"])
        elif item["item"] == "ThinLens":
            optical_item = op.ThinLens(
                nwaves=item["nwaves"],
                reference_wavelength=wavelength,
                radius=item["radius"],
            )
        elif item["item"] == "SquareAperture":
            optical_item = op.SquareAperture(size=item["size"])
        elif item["item"] == "RectangularAperture":
            optical_item = op.RectangleAperture(
                width=item["width"], height=item["height"]
            )  # m
        elif item["item"] == "HexagonAperture":
            optical_item = op.HexagonAperture(side=item["side"])
        elif item["item"] == "MultiHexagonalAperture":
            optical_item = op.MultiHexagonAperture(
                side=item["side"],
                rings=item["rings"],
                gap=item["gap"],
            )  # cm
        elif item["item"] == "SecondaryObscuration":
            optical_item = op.SecondaryObscuration(
                secondary_radius=item["secondary_radius"],
                n_supports=item["n_supports"],
                support_width=item["support_width"],
            )  # cm
        elif item["item"] == "ZernikeWFE":
            optical_item = op.ZernikeWFE(
                radius=item["radius"],
                coefficients=item["coefficients"],  # list of floats
                aperture_stop=item["aperture_stop"],
            )  # bool
        elif item["item"] == "SineWaveWFE":
            optical_item = op.SineWaveWFE(
                spatialfreq=item["spatialfreq"],  # 1/m
                amplitude=item["amplitude"],  # um
                rotation=item["rotation"],
            )
        else:
            raise NotImplementedError
        osys.add_pupil(optical_item)

    osys.add_detector(
        pixelscale=pixelscale,
        fov_arcsec=fov_arcsec,
    )

    psf: t.Tuple[
        t.List[fits.hdu.image.PrimaryHDU], t.List[op.Wavefront]
    ] = osys.calc_psf(
        wavelength=wavelength,
        return_intermediates=True,
        display_intermediates=display,
        normalize="last",
    )

    if display:
        plt.show()

    return psf


def optical_psf(
    detector: Detector,
    wavelength: float,
    fov_arcsec: float,
    pixelscale: float,
    optical_system: list,
) -> None:
    """Model function for poppy optics model: convolve photon array with psf.

    Parameters
    ----------
    detector: Detector
        Pyxel Detector object.
    wavelength: float
        Wavelength of incoming light in meters.
    fov_arcsec: float, optional
        Field Of View on detector plane in arcsec.
    pixelscale: float
        Pixel scale on detector plane (arcsec/pixel).
        Defines sampling resolution of PSF.
    optical_system:
        List of optical elements before detector with their specific arguments.

    Returns
    -------
    None
    """

    logging.getLogger("poppy").setLevel(
        logging.WARNING
    )  # TODO: Fix this. See issue #81

    psf = calc_psf(
        wavelength=wavelength,
        fov_arcsec=fov_arcsec,
        pixelscale=pixelscale,
        optical_system=optical_system,
    )

    # Convolution
    mean = np.mean(detector.photon.array)
    array = convolve_fft(
        detector.photon.array, psf[0][0].data, boundary="fill", fill_value=mean
    )

    detector.photon = Photon(array)
