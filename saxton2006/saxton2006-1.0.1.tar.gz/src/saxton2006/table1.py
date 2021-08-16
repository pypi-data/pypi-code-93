"""
Implementation of formalisms displayed in table1 of paper
"""
from math import log

soil_solid_density = 2.65
"""[g.cm-3] density of solid soil, gravels and the likes
"""


def bulk_density(tsat, stone_fraction):
    """Apparent bulk density of soil

    References:
        Eq.20 in Table 1 of Saxton & Rawls (2006) with apparently a bad
        definition of Rv unit :(

    Args:
        tsat (float): [m3.m-3] water content at saturation see :func:`theta_sat`
        stone_fraction (float): [m3.m-3] stone volumetric fraction between 0 and 1

    Returns:
        (float): [g.cm-3] bulk density of soil (gravels and matric)
    """
    return soil_solid_density * ((1 - tsat) * (1 - stone_fraction) + stone_fraction)


def theta_1500(clay_fraction, sand_fraction, organic_matter_fraction):
    """Compute soil moisture at permanent wilting point (-1.5 MPa).

    References:
        Eq.1 in Table 1 of Saxton & Rawls (2006)

    Args:
        clay_fraction (float): [g.g-1] weight ratio (between 0 and 1)
                               of clay as fraction of less than 2mm
        sand_fraction (float): [g.g-1] weight ratio (between 0 and 1)
                               of sand as fraction of less than 2mm
        organic_matter_fraction (float): [g.g-1] weight ratio (between 0 and 1)
                               of organic matter as fraction of less than 2mm

    Returns:
        (float): [m3.m-3] water content
    """
    # In the article, om_fraction is between 0 and 100
    # seems like they forgot to mention it :(
    om = organic_matter_fraction * 100

    theta1500t = (0.031
                  - 0.024 * sand_fraction
                  + 0.487 * clay_fraction
                  + 0.006 * om
                  + 0.005 * sand_fraction * om
                  - 0.013 * clay_fraction * om
                  + 0.068 * sand_fraction * clay_fraction)

    return theta1500t + 0.14 * theta1500t - 0.02


def theta_33(clay_fraction, sand_fraction, organic_matter_fraction):
    """Compute soil moisture at field capacity (-0.033 MPa).

    References:
        Eq.2 in Table 1 of Saxton & Rawls (2006)

    Args:
        clay_fraction (float): [g.g-1] weight ratio (between 0 and 1)
                               of clay as fraction of less than 2mm
        sand_fraction (float): [g.g-1] weight ratio (between 0 and 1)
                               of sand as fraction of less than 2mm
        organic_matter_fraction (float): [g.g-1] weight ratio (between 0 and 1)
                               of organic matter as fraction of less than 2mm

    Returns:
        (float): [m3.m-3] water content
    """
    # In the article, om_fraction is between 0 and 100
    # seems like they forgot to mention it :(
    om = organic_matter_fraction * 100

    theta33t = (0.299
                - 0.251 * sand_fraction
                + 0.195 * clay_fraction
                + 0.011 * om
                + 0.006 * sand_fraction * om
                - 0.027 * clay_fraction * om
                + 0.452 * sand_fraction * clay_fraction)

    return theta33t + 1.283 * theta33t ** 2 - 0.374 * theta33t - 0.015


def theta_s_minus_33(clay_fraction, sand_fraction, organic_matter_fraction):
    """SAT-33 kPa moisture.

    References:
        Eq.3 in Table 4 of Saxton & Rawls (2006)

    Args:
        clay_fraction (float): [g.g-1] weight ratio (between 0 and 1)
                               of clay as fraction of less than 2mm
        sand_fraction (float): [g.g-1] weight ratio (between 0 and 1)
                               of sand as fraction of less than 2mm
        organic_matter_fraction (float): [g.g-1] weight ratio (between 0 and 1)
                               of organic matter as fraction of less than 2mm

    Returns:
        (float): [MPa] water potential
    """
    # In the article, om_fraction is between 0 and 100
    # seems like they forgot to mention it :(
    om = organic_matter_fraction * 100

    theta_s33t = (0.078
                  + 0.278 * sand_fraction
                  + 0.034 * clay_fraction
                  + 0.022 * om
                  - 0.018 * sand_fraction * om
                  - 0.027 * clay_fraction * om
                  - 0.584 * sand_fraction * clay_fraction)

    return theta_s33t + 0.636 * theta_s33t - 0.107


def bubbling_pressure(clay_fraction, sand_fraction, organic_matter_fraction):
    """Tension at air entry.

    References:
        Eq.4 in Table 4 of Saxton & Rawls (2006)

    Args:
        clay_fraction (float): [g.g-1] weight ratio (between 0 and 1)
                               of clay as fraction of less than 2mm
        sand_fraction (float): [g.g-1] weight ratio (between 0 and 1)
                               of sand as fraction of less than 2mm
        organic_matter_fraction (float): [g.g-1] weight ratio (between 0 and 1)
                               of organic matter as fraction of less than 2mm

    Returns:
        (float): [MPa] water potential at saturation
    """
    theta_s33 = theta_s_minus_33(clay_fraction, sand_fraction, organic_matter_fraction)

    psi_et = (27.16
              - 21.67 * sand_fraction
              - 27.93 * clay_fraction
              - 81.97 * theta_s33
              + 71.12 * sand_fraction * theta_s33
              + 8.29 * clay_fraction * theta_s33
              + 14.05 * sand_fraction * clay_fraction)

    psi_e = psi_et + 0.02 * psi_et ** 2 - 0.113 * psi_et - 0.7
    return -psi_e * 1e-3  # [kPa] to [MPa]


def theta_sat(clay_fraction, sand_fraction, organic_matter_fraction):
    """Compute soil moisture at saturation (0 MPa).

    References:
        Eq.5 in Table 1 of Saxton & Rawls (2006)

    Args:
        clay_fraction (float): [g.g-1] weight ratio (between 0 and 1)
                               of clay as fraction of less than 2mm
        sand_fraction (float): [g.g-1] weight ratio (between 0 and 1)
                               of sand as fraction of less than 2mm
        organic_matter_fraction (float): [g.g-1] weight ratio (between 0 and 1)
                               of organic matter as fraction of less than 2mm

    Returns:
        (float): [m3.m-3] water content
    """
    th_s33 = theta_s_minus_33(clay_fraction, sand_fraction, organic_matter_fraction)
    th_33 = theta_33(clay_fraction, sand_fraction, organic_matter_fraction)

    return th_33 + th_s33 - 0.097 * sand_fraction + 0.043


def matric_potential(theta, th_sat, th_33, th_1500, psi_e):
    """Water tension.

    References:
        Eq.11->15 in Table 1 of Saxton & Rawls (2006)

    Args:
        theta (float): [m3.m-3] water content
        th_sat (float): [m3.m-3] soil moisture content at saturation
        th_33 (float): [m3.m-3] soil moisture content at field capacity
        th_1500 (float): [m3.m-3] soil moisture content at plant wilting point
        psi_e (float): [MPa] bubbling pressure

    Returns:
        (float): [MPa]
    """
    psi_fc = -33e-3  # [MPa] water potential at field capacity

    if theta < th_1500:
        raise NotImplementedError

    if theta <= th_33:  # eq 11
        b = log(1500 / 33) / log(th_33 / th_1500)
        return psi_fc * (th_33 / theta) ** b

    if theta <= th_sat:  # eq 12
        return psi_fc - (psi_fc - psi_e) * (theta - th_33) / (th_sat - th_33)

    return psi_e  # theta > th_sat, eq 13


def water_conductance_sat(th_sat, th_33, th_1500):
    """Soil water conductance at saturation.

    References:
        Eq.16 in Table 1 of Saxton & Rawls (2006)

    Args:
        th_sat (float): [m3.m-3] soil moisture content at saturation
        th_33 (float): [m3.m-3] soil moisture content at field capacity
        th_1500 (float): [m3.m-3] soil moisture content at plant wilting point

    Returns:
        (float): [mm.h-1]
    """
    b = log(1500 / 33) / log(th_33 / th_1500)
    lam = 1 / b

    return 1930 * (th_sat - th_33) ** (3 - lam)


def water_conductance(theta, th_sat, th_33, th_1500, k_sat):
    """Soil water conductance.

    Args:
        theta (float): [m3.m-3] water content
        th_sat (float): [m3.m-3] soil moisture content at saturation
        th_33 (float): [m3.m-3] soil moisture content at field capacity
        th_1500 (float): [m3.m-3] soil moisture content at plant wilting point
        k_sat (float): [mm.h-1] water conductance at saturation

    Returns:
        (float): [mm.h-1]
    """
    if theta >= th_sat:
        return k_sat

    b = log(1500 / 33) / log(th_33 / th_1500)
    return k_sat * (theta / th_sat) ** (3 + 2 * b)
