from enum import Enum


class MeasurementType(str, Enum):
    GammaRay = ("GammaRay",)
    Caliper = ("Caliper",)
    Resistivity = ("Resistivity",)
    Density = ("Density",)
    Neutron = ("Neutron",)
    PPFG = ("PPFG",)
    Geomechanics = ("Geomechanics",)
    Core = ("Core",)
