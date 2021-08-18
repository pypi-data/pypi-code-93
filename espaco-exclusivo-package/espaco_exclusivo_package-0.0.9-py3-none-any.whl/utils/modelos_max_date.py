# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description: 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.: 

    Author:           @diego.yosiura
    Last Update:      23/07/2021 18:04
    Created:          23/07/2021 18:04
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco-exclusivo-package
    IDE:              PyCharm
"""
from datetime import datetime
from datetime import timedelta

from ..produtos.meteorologia import Modelos
from ..produtos.meteorologia import DiasModelos


def check_global_max_date() -> datetime:
    n_max = 0
    for m in DiasModelos:
        if m.value > n_max:
            n_max = m.value
    return datetime(datetime.now().year, datetime.now().month, datetime.now().day) + timedelta(days=n_max)


def check_modelo_max_date(modelo: Modelos) -> datetime:
    m = getattr(DiasModelos, modelo.name)
    if m is None:
        return None
    return datetime(datetime.now().year, datetime.now().month, datetime.now().day) + timedelta(days=m.value)
