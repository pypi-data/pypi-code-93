# -*- coding: utf-8 -*-
"""
Functions related to modelling of energy assets.

This file can also be imported as a module and contains the following
functions:

    * pv_module - convert solar irradiance to the power output of a PV installation


References:
    J. Twidell & T. Weir, Renewable Energy Resources, 2nd edition, 
    Taylor and Francis, 2006

"""

# Import all useful libraries
import numpy as np


def pv_module(incident_radiation, rated_power=1000, rated_radiation=1000):
    """Models the power production curve of a standard solar PV panel.
    The model is based upon a simplified linear model.

    Parameters
    ----------
    incident_radiation : np.array
        Values of the incident radiation on the panel [W/m^2]
    rated_power : float
        Rated power of the inverter of the PV panel [W]
        (default: 1000)
    rated_radiation : float
        Values of the design radiation on the panel [W/m^2]
        (default: 1000)

    Raises
    ------
    None

    Returns
    -------
    power_output : np.array
        Power production corresponding to the values of incident_radiation [W]
    """
    power_output = rated_power * (incident_radiation / rated_radiation)

    # Forcing the output to not exceed the rated power
    k_excess = np.where(power_output > rated_power)
    power_output[
        k_excess,
    ] = rated_power

    return power_output
