# -*- coding: utf-8 -*-
from django.db import connections


class Query(object):
    def __init__(self, sql):
        self.sql = sql
        self._resultados = []

    def __getitem__(self, item):
        return self.resultado[item]

    def __nonzero__(self):
        return len(self._resultados) > 0

    @property
    def resultado(self):
        if self.tem_resultados:
            return self._resultados[0]
        return {}

    @property
    def resultados(self):
        if self.tem_resultados:
            return self._resultados
        return []

    def executar(self, *args):
        return self.executar_db("default", *args)

    def executar_db(self, db, *args):
        cursor = connections[db].cursor()
        cursor.execute(self.sql, args)
        desc = cursor.description

        if cursor.statusmessage.startswith("INSERT") \
                or cursor.statusmessage.startswith("UPDATE") \
                or cursor.statusmessage.startswith("DELETE"):
            return self

        self._resultados = [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]

        return self

    @property
    def tem_resultados(self):
        return len(self._resultados) > 0


# class QueryMock(Query):
#     """
#     Serve para fazer um mock simples do resultado do Query
#     """
#
#     def executar(self, *args):
#         r = self.mock()
#         if isinstance(r, list):
#             self._resultados = r
#         else:
#             self._resultados = [r]
#         return self
#
#     def mock(self):
#         """
#         Responsável por retornar o resultado que será usado no mock
#         """
#         return {}