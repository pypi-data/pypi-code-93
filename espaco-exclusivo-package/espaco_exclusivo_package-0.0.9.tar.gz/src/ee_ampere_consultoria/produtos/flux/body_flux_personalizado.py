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

from ... import Configuration
from ...utils import check_global_max_date

from ..meteorologia import Modelos

from . import BodyFluxPersonalizadoCenario
from . import BodyFluxPersonalizadoCenarioBloco


class BodyFluxPersonalizado:
    __ds_nome_estudo = None
    __ds_nome_cenario = None
    __dt_inicio = None
    __dt_fim = None
    __cenarios = None

    def set_nome_estudo(self, nome: str):
        self.__ds_nome_estudo = re.sub(r'[^A-z0-9_-]', '', str(nome).upper())
        if len(self.__ds_nome_estudo) <= 3:
            raise Exception("[EE BodyFluxPersonalizado] - O nome do estudo deve conter "
                            "mais de 3 caracteres válidos. [{}]".format(self.__ds_nome_estudo))
        self.__ds_nome_cenario = self.__ds_nome_estudo

        if self.__cenarios is not None:
            self.__cenarios[0].ds_nome = self.__ds_nome_cenario

    def set_periodo_analise(self, inicio: datetime, fim: datetime):
        inicio = datetime(inicio.year, inicio.month, inicio.day)
        fim = datetime(fim.year, fim.month, fim.day)

        if fim > check_global_max_date():
            raise Exception("[EE BodyFluxPersonalizado] - O fim do estudo {} excede o "
                            "período máximo de estudo {}.".format(fim, check_global_max_date()))

        if inicio.timestamp() <= datetime(datetime.now().year, datetime.now().month, datetime.now().day).timestamp():
            raise Exception("[EE BodyFluxPersonalizado] - O inicio do estudo deve ser maior que a data de hoje.")
        if fim <= inicio:
            raise Exception("[EE BodyFluxPersonalizado] - O fim do estudo deve ser maior que a data de inicio.")
        self.__dt_inicio = inicio
        self.__dt_fim = fim

    def add_bloco(self, ds_modelo: Modelos, ck_rmv: bool, dt_data_prev: datetime,
                  dt_inicio: datetime, dt_fim: datetime):
        try:
            dt_data_prev = datetime(dt_data_prev.year, dt_data_prev.month, dt_data_prev.day)
            dt_inicio = datetime(dt_inicio.year, dt_inicio.month, dt_inicio.day)
            dt_fim = datetime(dt_fim.year, dt_fim.month, dt_fim.day)

            if self.__cenarios is None:
                self.__cenarios = []
            if len(self.__cenarios) <= 0:
                self.__cenarios.append(BodyFluxPersonalizadoCenario())
                self.__cenarios[0].ds_nome = self.__ds_nome_cenario

            self.__cenarios[0].add_bloco(ds_modelo, dt_data_prev, ck_rmv, dt_inicio, dt_fim)
        except Exception as e:
            error = "[EE BodyFluxPersonalizado] - Erro não tratado: {}".format(str(e))
            Configuration.debug_print(error, e)
            raise Exception(error)

    def get_json(self):
        json_response = {
            'ds_nome_estudo': self.__ds_nome_estudo,
            'ds_nome_cenario': self.__ds_nome_cenario,
            'dt_inicio': self.__dt_inicio.timestamp(),
            'dt_fim': self.__dt_fim.timestamp(),
            'cenarios': [],
        }

        for c in self.__cenarios:
            c.validate()
            blocos = []
            if c.blocos[0].dt_inicio != self.__dt_inicio or c.blocos[-1].dt_fim != self.__dt_fim:
                raise Exception("Os blocos de cada cenário devem compreender todo o período de estudo. "
                                "{} - {} | Inicio Bloco 01 [{}] | Fim Bloco n [{}]".format(self.__dt_inicio,
                                                                                           self.__dt_fim,
                                                                                           c.blocos[0].dt_inicio,
                                                                                           c.blocos[-1].dt_fim))
            for b in c.blocos:
                blocos.append({
                    "ds_modelo": b.ds_modelo.value,
                    "dt_data_prev": b.dt_data_prev.timestamp(),
                    "ck_rmv": b.ck_rmv,
                    "dt_inicio": b.dt_inicio.timestamp(),
                    "dt_fim": b.dt_fim.timestamp()
                })

            json_response['cenarios'].append({'ds_nome': c.ds_nome, 'blocos': blocos})
        return json_response
