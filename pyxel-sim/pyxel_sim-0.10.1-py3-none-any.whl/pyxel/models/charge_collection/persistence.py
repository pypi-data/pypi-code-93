#  Copyright (c) YOUR COPYRIGHT HERE

"""
persistence module for the PyXel simulation.

This module is used in charge_collection

-------------------------------------------------------------------------------

+--------------+----------------------------------+---------------------------+
| Author       | Name                             | Creation                  |
+--------------+----------------------------------+---------------------------+
| You          | charge_collection                | 05/20/2021                |
+--------------+----------------------------------+---------------------------+

+-----------------+-------------------------------------+---------------------+
| Contributor     | Name                                | Creation            |
+-----------------+-------------------------------------+---------------------+
| Name            | filename                            | -                   |
+-----------------+-------------------------------------+---------------------+

This module can be found in pyxel/models/charge_collection/persistence.py

Algorithm
=========

The persistence model take as input the total number of detrapped charges
(persistence map with a 10000 seconds soak at more than the FWC) and a map
which is the previous one divided by full well capacity. This gives the total
amount of trap per charge.

At each iteration of the pipeline, the model will first check if there is a
'persistence' entry in the memore of the detector and if not will create it
(happens only at the first iteration).
Then, it will compute the amount of trapped charges in this iteration, add it
to the memory of the detector and then will remove this amount from the pixel array.

Default parameter
=================

The defaults parameter are the one derived from the characterization of the ENG grade
detector for MOONS (H4RG).

+----------------+-------------+
| Time constants | Proportions |
+================+=============+
| 1              | 0.307       |
+----------------+-------------+
| 10             | 0.175       |
+----------------+-------------+
| 100            | 0.188       |
+----------------+-------------+
| 1000           | 0.136       |
+----------------+-------------+
| 10000          | 0.194       |
+----------------+-------------+

Code example
============

.. code-block:: python

    # To access the memory of the detector with the persistence map

    detector._memory["persistence"]

    # This dictionnary consist of 5 entries (one per time constant)

.. literalinclude:: pyxel/models/charge_collection/persistence.py
    :language: python
    :linenos:
    :lines: 84-87

Model reference in the YAML config file
=======================================

.. code-block:: yaml

    pipeline:

      # Persistence model based on MOONS detector (H4RG) measurements
      - name: persistence
        func: pyxel.models.charge_collection.persistence.current_persistence
        enabled: true
        arguments:
          trap_timeconstants: [1, 10, 100, 1000, 10000]
          trap_densities: data/fits/20210408121614_20210128_ENG20370_AUTOCHAR-Persistence_FitTrapDensityMap.fits
          trap_max: data/fits/20210408093114_20210128_ENG20370_AUTOCHAR-Persistence_FitMaximumTrapMap.fits
          trap_proportions: [0.307, 0.175, 0.188, 0.136, 0.194]

Useful links
============

Persistence paper from S. Tulloch
https://arxiv.org/abs/1908.06469

ReadTheDocs documentation
https://sphinx-rtd-theme.readthedocs.io/en/latest/index.html

.. todo::

   - Add temperature dependency
   - Add default -flat?- trap maps

"""

import logging

import numpy as np
from astropy.io import fits

from pyxel.detectors import CMOS


# @validators.validate
# @config.argument(name='', label='', units='', validate=)
def simple_persistence(
    detector: CMOS, trap_timeconstants: list, trap_densities: list
) -> None:
    """Trapping/detrapping charges."""
    logging.info("Persistence")
    if "persistence" not in detector._memory.keys():
        detector._memory["persistence"] = dict()
        for trap_density, trap_timeconstant in zip(trap_densities, trap_timeconstants):
            entry = "".join(
                ["trappedCharges_", str(trap_density), "-", str(trap_timeconstant)]
            )
            detector._memory["persistence"].update(
                {entry: np.zeros((detector.geometry.row, detector.geometry.col))}
            )
    else:
        for trap_density, trap_timeconstant in zip(trap_densities, trap_timeconstants):
            entry = "".join(
                ["trappedCharges_", str(trap_density), "-", str(trap_timeconstant)]
            )
            trapped_charges = detector._memory["persistence"][entry]
            # Trap density is a scalar for now, in the future we could feed maps?
            # the delta t is fixed to 0.5 s, need to find a way to avoid problem of divergence
            trapped_charges = trapped_charges + (0.5 / trap_timeconstant) * (
                detector.pixel.array * trap_density - trapped_charges
            )
            # Remove the trapped charges from the pixel
            detector.pixel.array -= trapped_charges.astype(np.int32)
            # Replace old trapped charges map in the detector's memory
            detector._memory["persistence"][entry] = trapped_charges

    return None


def current_persistence(
    detector: CMOS,
    trap_timeconstants: list,
    trap_densities: str,
    trap_max: str,
    trap_proportions: list,
) -> None:
    """Trapping/detrapping charges."""
    logging.info("Persistence")
    # If the file for trap density is correct open it and use it
    # otherwise I need to define a default trap density map

    # Extract trap density / full well
    trap_densities_2d = fits.open(trap_densities)[0].data[
        : detector.geometry.row, : detector.geometry.col
    ]  # type: np.ndarray
    trap_densities_2d[np.where(trap_densities_2d < 0)] = 0

    # Extract the max amount of trap by long soak
    trap_max_2d = fits.open(trap_max)[0].data[
        : detector.geometry.row, : detector.geometry.col
    ]
    trap_max_2d[np.where(trap_max_2d < 0)] = 0

    # If there is no entry for persistence in the memory of the detector
    # create one
    if "persistence" not in detector._memory.keys():
        detector._memory["persistence"] = dict()
        for trap_proportion, trap_timeconstant in zip(
            trap_proportions, trap_timeconstants
        ):
            entry = "".join(
                ["trappedCharges_", str(trap_proportion), "-", str(trap_timeconstant)]
            )
            detector._memory["persistence"].update(
                {entry: np.zeros((detector.geometry.row, detector.geometry.col))}
            )
            trapped_charges = detector._memory["persistence"][entry]

    # For each trap population
    for trap_proportion, trap_timeconstant in zip(trap_proportions, trap_timeconstants):

        # Get the correct persistence traps entry
        entry = "".join(
            ["trappedCharges_", str(trap_proportion), "-", str(trap_timeconstant)]
        )

        # Select the trapped charges array
        trapped_charges = detector._memory["persistence"][entry]

        # Time for reading a frame
        # delta_t = (detector.geometry.row * detector.geometry.col)/detector.characteristics.readout_freq
        delta_t = detector.time_step

        # Computer trapped charge for this increament of time
        # Time factor is the integration time divided by the time constant (1, 10, 100, 1000, 10000)
        time_factor = delta_t / trap_timeconstant

        # Amount of charges trapped per unit of full well
        max_charges = trap_densities_2d * trap_proportion

        # Maximum of amount of charges trapped
        fw_trap = trap_max_2d * trap_proportion

        diff = time_factor * (
            max_charges * detector.pixel.array * np.exp(-time_factor) - trapped_charges
        )
        # Compute trapped charges
        trapped_charges = trapped_charges + time_factor * (
            max_charges * detector.pixel.array * np.exp(-time_factor) - trapped_charges
        )

        # When the amount of trapped charges is superior to the maximum of available traps, set to max
        trapped_charges[np.where(trapped_charges > fw_trap)] = max_charges[
            np.where(trapped_charges > fw_trap)
        ]
        # Can't have a negative amount of charges trapped
        trapped_charges[np.where(trapped_charges < 0)] = 0

        # Remove the trapped charges from the pixel
        # detector.pixel.array -= trapped_charges.astype(np.int32)
        detector.pixel.array -= diff.astype(np.int32)

        # Replace old trapped charges map in the detector's memory
        detector._memory["persistence"][entry] = trapped_charges

    return None
