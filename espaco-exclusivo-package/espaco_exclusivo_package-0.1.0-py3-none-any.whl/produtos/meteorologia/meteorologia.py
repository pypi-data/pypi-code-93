# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description: 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.: 

    Author:           @diego.yosiura
    Last Update:      21/07/2021 16:09
    Created:          21/07/2021 16:09
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco_exclusivo_package
    IDE:              PyCharm
"""
from json import dumps

from ... import Produto
from ... import Configuration
from . import Prazo
from . import BodyComparador
from . import BodyChuvaObservada
from ..base_produto import BaseProduto


class Meteorologia(BaseProduto):
    def get_images(self, prazo: Prazo, dia: int, mes: int, ano: int, index: int) -> dict:
        """
        Retorna um dicionário contendo as imagens de curto, médio ou longo prazo no formato base64.

        :param prazo: [cp, mp ou lp]
        :type prazo: Prazo
        :param dia: Dia em que a previsão foi feita
        :type dia: int
        :param mes: Mês em que a previsão foi feita
        :type mes: int
        :param ano: Ano em que a previsão foi feita
        :type ano: int
        :param index: Número que corresponde ao dia da previsão, de 1 -> Máximo de dias de cada modelo.
        :type index: int
        :return: dict
        """
        try:
            p_key = self.request.request_prod_key(Produto.METEOROLOGIA.value)
            response = self.request.request_json('meteorologia.get_images?'
                                                 'product_key={}&'
                                                 'tipo={}&'
                                                 'day={}&'
                                                 'month={}&'
                                                 'year={}&'
                                                 'index={}'.format(p_key,
                                                                    prazo.value, dia, mes, ano, index), '')
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']
            return None
        except Exception as e:
            error = "[EE Meteorologia] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def comparar(self, body_comparador: BodyComparador) -> dict:
        """
        Compara dois modelos com base nos parâmetros informados no objeto BodyComparador.


        :param body_comparador: Corpo da requisição com as informações de comparação.
        :type body_comparador: BodyComparador
        :return: dict
        """
        try:
            p_key = self.request.request_prod_key(Produto.METEOROLOGIA.value)
            response = self.request.request_json('meteorologia.comparador?product_key={}'.format(p_key),
                                                 dumps({
                                                     "method": "solicitar_comparacao",
                                                     "params": {
                                                         "tipo": "comparacao",
                                                         "comparacao": body_comparador.get_json()
                                                     },
                                                     "broadcast": False,
                                                     "room": "",
                                                     "user": "exclusivo_comparador_client"
                                                 }))
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']['params']
            return None
        except Exception as e:
            error = "[EE Meteorologia] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def chuva_observada(self, body_chuva_observada: BodyChuvaObservada) -> dict:
        """

        :param body_chuva_observada:
        :param body_comparador: Corpo da requisição com as informações de comparação.
        :type body_comparador: BodyComparador
        :return: dict
        """
        try:
            p_key = self.request.request_prod_key(Produto.METEOROLOGIA.value)
            response = self.request.request_json('meteorologia.comparador?product_key={}'.format(p_key),
                                                 dumps({
                                                     "method": "solicitar_comparacao",
                                                     "params": {
                                                         "tipo": "acumulado",
                                                         "acumulado": body_chuva_observada.get_json()
                                                     },
                                                     "broadcast": False,
                                                     "room": "",
                                                     "user": "exclusivo_comparador_client"
                                                 }))
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']['params']
            return None
        except Exception as e:
            error = "[EE Meteorologia] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)
