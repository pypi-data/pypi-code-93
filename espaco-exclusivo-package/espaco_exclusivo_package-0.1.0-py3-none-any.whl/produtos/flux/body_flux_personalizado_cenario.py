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
import re

from datetime import datetime
from datetime import timedelta

from ... import Configuration
from ..meteorologia import Modelos

from . import BodyFluxPersonalizadoCenarioBloco


class BodyFluxPersonalizadoCenario:
    ds_nome = None
    blocos = None

    def add_bloco(self, ds_modelo: Modelos, dt_data_prev: datetime, ck_rmv: bool,
                  dt_inicio: datetime, dt_fim: datetime):
        try:
            dt_data_prev = datetime(dt_data_prev.year, dt_data_prev.month, dt_data_prev.day)
            dt_inicio = datetime(dt_inicio.year, dt_inicio.month, dt_inicio.day)
            dt_fim = datetime(dt_fim.year, dt_fim.month, dt_fim.day)

            if self.blocos is None:
                self.blocos = []

            for bloco in self.blocos:
                if bloco.dt_inicio >= dt_inicio and dt_inicio <= bloco.dt_fim:
                    raise Exception("[EE BodyFluxPersonalizadoCenario] - O inicio sobrescreve o"
                                    " período de um dos blocos {} - Bloco {}.".format(dt_inicio, bloco.ds_modelo))
                if bloco.dt_inicio >= dt_fim and dt_fim <= bloco.dt_fim:
                    raise Exception("[EE BodyFluxPersonalizadoCenario] - O fim sobrescreve o"
                                    " período de um dos blocos {} - Bloco {}.".format(dt_fim, bloco.ds_modelo))

            bl = BodyFluxPersonalizadoCenarioBloco(ds_modelo, dt_data_prev, ck_rmv, dt_inicio, dt_fim)
            self.blocos.append(bl)
            self.validate()
        except Exception as e:
            error = "[EE BodyFluxPersonalizadoCenario] - Erro não tratado: {}".format(str(e))
            Configuration.debug_print(error, e)
            raise Exception(error)

    def validate(self):
        if self.ds_nome is None:
            raise Exception("[EE BodyFluxPersonalizadoCenario] - O nome do cenário não pode ser nulo.")
        self.ds_nome = re.sub(r'[^A-z0-9_-]', '', str(self.ds_nome).upper())
        if len(self.ds_nome) <= 3:
            raise Exception("[EE BodyFluxPersonalizadoCenario] - O nome do cenário deve conter "
                            "mais de 3 caracteres válidos. [{}]".format(self.ds_nome))

        self.sort_blocos()

        for i in range(0, len(self.blocos) - 1):
            self.blocos[i].validate()

            n_day = self.blocos[i].dt_fim + timedelta(days=1)
            if self.blocos[i + 1].dt_inicio.day != n_day.day or \
                    self.blocos[i + 1].dt_inicio.month != n_day.month or \
                    self.blocos[i + 1].dt_inicio.year != n_day.year:
                raise Exception("[EE BodyFluxPersonalizadoCenario] - Os blocos devem ser contínuos, o inicio"
                                " do bloco [{}] deve ser o proximo dia do bloco {}.".format(i + 1, i))

    def sort_blocos(self):
        self.blocos.sort(reverse=False, key=BodyFluxPersonalizadoCenario.__fn_sort_blocos)

    @staticmethod
    def __fn_sort_blocos(bloco):
        return bloco.dt_inicio.timestamp()
