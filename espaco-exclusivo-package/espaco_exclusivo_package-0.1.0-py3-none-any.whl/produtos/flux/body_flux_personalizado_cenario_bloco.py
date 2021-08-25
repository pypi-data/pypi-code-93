# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description: 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.: 

    Author:           @diego.yosiura
    Last Update:      23/07/2021 16:57
    Created:          23/07/2021 16:57
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco-exclusivo-package
    IDE:              PyCharm
"""
from datetime import datetime
from ..meteorologia import Modelos
from ...utils import check_modelo_max_date


class BodyFluxPersonalizadoCenarioBloco:
    ds_modelo = None
    dt_data_prev = None
    ck_rmv = None
    dt_inicio = None
    dt_fim = None

    def __init__(self, ds_modelo: Modelos, dt_data_prev: datetime, ck_rmv: bool,
                 dt_inicio: datetime, dt_fim: datetime):
        self.ds_modelo = ds_modelo
        self.dt_data_prev = dt_data_prev
        self.ck_rmv = ck_rmv
        self.dt_inicio = dt_inicio
        self.dt_fim = dt_fim
        self.validate()

    def validate(self):

        found = False

        for m in Modelos:
            if m.value == self.ds_modelo.value:
                found = True

        if not found:
            raise Exception("[EE BodyFluxPersonalizadoCenario] - O modelo {} não é válido".format(self.ds_modelo))

        modelo_max_date = check_modelo_max_date(self.ds_modelo)
        if modelo_max_date is None:
            raise Exception("[EE BodyFluxPersonalizadoCenario] - O modelo {} não está especificado com uma "
                            "data máxima válida, entre emc ontato com o suporte".format(self.ds_modelo))

        if self.dt_data_prev.timestamp() >= datetime.now().timestamp():
            raise Exception("[EE BodyFluxPersonalizadoCenario] - A data {} deve ser anterior "
                            "à hoje.".format(self.dt_data_prev))

        if type(self.ck_rmv) != bool:
            raise Exception("[EE BodyFluxPersonalizadoCenario] - O valor de remoção de viés {} deve ser "
                            "booleano válido.".format(self.ck_rmv))

        if self.dt_inicio.timestamp() <= datetime.now().timestamp():
            raise Exception("[EE BodyFluxPersonalizadoCenario] - O inicio do período de previsão deve "
                            "ser maior que hoje {}.".format(self.dt_inicio))

        if self.dt_inicio.timestamp() >= self.dt_fim.timestamp():
            raise Exception("[EE BodyFluxPersonalizadoCenario] - O inicio do período de previsão deve "
                            "ser menos que o fim do período {} - {}.".format(self.dt_inicio, self.dt_fim))

        if self.dt_fim.timestamp() > modelo_max_date.timestamp():
            raise Exception("[EE BodyFluxPersonalizadoCenario] - O fom do período excede o máximo ({}) para o modelo "
                            "{} - {}.".format(modelo_max_date, self.ds_modelo.name, self.dt_fim))
