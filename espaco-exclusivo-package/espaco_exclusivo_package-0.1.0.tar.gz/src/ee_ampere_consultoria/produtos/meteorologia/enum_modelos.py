# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description: 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.: 

    Author:           @diego.yosiura
    Last Update:      21/07/2021 19:49
    Created:          21/07/2021 19:49
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco_exclusivo_package
    IDE:              PyCharm
"""
from enum import Enum


class Modelos(Enum):
    WRF = 'wrf'
    COSMO = 'cosmo'
    UKMO = 'ukmo'
    ICON = 'icon'
    ECMWF = 'ecmwf'
    GEM = 'gem'
    ACCESSG = 'accessg'
    ETA = 'eta'
    AMPERE = 'ampere'
    PREVC = 'prevc'
    NPREVC = 'nprevc'
    ECMWFENS = 'ecmwfens'
    GEFS = 'gefs'
    GFS = 'gfs'
    ECMWF46 = 'ecmwf46'
    MEMBROS_00 = 'membros_00'
    MEMBROS_06 = 'membros_06'
    MEMBROS_12 = 'membros_12'
    MEMBROS_18 = 'membros_18'
    TROPICAL = 'tropical'
    INFORMES = 'informes'
    ZERO = 'zero'
    CLIMATOLOGIA = 'climatologia'
    MERGE = 'merge'
