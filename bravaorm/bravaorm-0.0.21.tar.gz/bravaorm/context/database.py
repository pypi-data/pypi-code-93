# -*- coding: utf-8 -*-
import mysql.connector as mariadb
from bravaorm.utils.log import *

class DataBase():

    # Init
    def __init__(self, db_user=None, db_password=None, db_host=None, db_port=None, db_database=None, db_ssl=False, db_ssl_ca=None, db_ssl_cert=None, db_ssl_key=None, db_charset='utf8'):
        try:

            Debug(f"Starting DB Connection at {db_host}:{db_port}")

            self._charset = db_charset
            if not db_ssl:
                self._conn = mariadb.connect(
                    user=db_user, password=db_password, host=db_host, port=db_port, database=db_database, use_unicode=True)
            else:
                self._conn = mariadb.connect(user=db_user, password=db_password, host=db_host, port=db_port,
                                             database=db_database, ssl_ca=db_ssl_ca, ssl_cert=db_ssl_cert, ssl_key=db_ssl_key, use_unicode=True)
        # ERRO CONEXÃO COM BANCO DE DADOS
        except mariadb.Error as e:
            Error('Connection', e)
            raise e
        # ERRO GENÉRICO
        except Exception as e:
            Error('Connection', e)
            raise e

    # INICIA CURSOR
    @property
    def cursor(self):
        try:
            Debug(f"Create new Cursor")
            cursor = self._conn.cursor(dictionary=True)
            return cursor
        except mariadb.Error as e:
            Error('Cursor', e)
            raise e
        except Exception as e:
            Error('Cursor', e)
            raise e

    # FECHA CONEXÃO
    def close(self):
        try:
            Debug(f"Connection DB closed")
            self._conn.close()
        # ERRO EM FECHAMENTO CONEXÃO COM BANCO DE DADOS
        except mariadb.Error as e:
            Error('Close Connection', e)
            raise e
        # ERRO GENÉRICO EM FECHAMENTO CONEXÃO COM BANCO DE DADOS
        except Exception as e:
            Error('Close Connection', e)
            raise e

    # EXECUÇÃO SELECT SQL
    def fetchall(self, sql_query):
        cursor = self.cursor
        try:
            Debug(f"Fetching Data")
            Debug(f"Query: {sql_query}")
            cursor.execute(sql_query)
            try:
                registros = cursor.fetchall()
                Debug(f"Results: {len(registros)}")
            except Exception as e:
                registros = []
            return registros
        except mariadb.Error as e:
            Error('Fetching Data', e)
            raise e
        except Exception as e:
            Error('Fetching Data', e)
            raise e
        finally:
            cursor.close()
            Debug(f"Cursor Closed")

    # EXECUÇÃO SELECT SQL
    def fetchone(self, sql_query):
        cursor = self.cursor
        try:
            Debug(f"Fetching Data")
            Debug(f"Query: {sql_query}")
            cursor.execute(sql_query)
            try:
                registros = cursor.fetchone()
                Debug(f"Results: {len(registros)}")
            except Exception as e:
                registros = []
            return registros
        except mariadb.Error as e:
            Error('Fetching Data', e)
            raise e
        except Exception as e:
            Error('Fetching Data', e)
            raise e
        finally:
            Debug(f"Cursor Closed")
            cursor.close()

    # EXECUÇÃO SELECT SQL
    def save(self, sql_statement, data):

        cursor = self.cursor
        try:
            Debug(f"Saving Data")
            Debug(f"Query: {sql_statement}")
            Debug(f"Data: {data}")
            cursor.execute(sql_statement, data)
            return cursor.lastrowid if cursor.lastrowid > 0 else None
        except mariadb.Error as e:
            Error('Saving Data', e)
            raise e
        except Exception as e:
            Error('Saving Data', e)
            raise e
        finally:
            cursor.close()

    def commit(self):
        try:
            Debug(f"Commit Actions")
            self._conn.commit()
        except Exception as e:
            Error('Commit', e)
            Debug(f"Rollback Error")
            self._conn.rollback()
