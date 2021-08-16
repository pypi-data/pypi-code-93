# -*- coding: utf-8 -*-
"""
Functions related to modelling of energy assets.

This file can also be imported as a module and contains the following
functions:

    [None] Refer to package "senasopt" on PyPi

Note: the previous functions have been deprecated.

"""

from seedftw.exceptions import MovedToSenasopt


def __moved_to_senasopt(new_function):
    raise MovedToSenasopt(new_function)


def wind_turbine_generator(*args):
    __moved_to_senasopt(new_function="wind.wind_turbine")


def solar_pv_generator(*args):
    __moved_to_senasopt(new_function="solar.pv_module")


def battery_optimal_controller(*args):
    __moved_to_senasopt(new_function="battery.battery_optimal_controller")
