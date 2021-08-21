

## Twitter: @sparkle_twtt : https://twitter.com/sparkle_twtt
## Medium: @sparkle_mdm : https://sparkle-mdm.medium.com
## YouTube: https://www.youtube.com/channel/UC19jAflhuZEtmrYYrlhX-6w?view_as=subscriber
## E-mail: sparkle.official.01@gmail.com
## Yoshio Yamauchi (SPARKLE)



# Feb 27, 2021
# #proxy #tor #onion #routing #onion_routing #scraping #scrape
# #stem #anonymize #anonymization #change_url
# https://gist.github.com/DusanMadar/8d11026b7ce0bce6a67f7dd87b999f6b
# https://gist.github.com/KhepryQuixote/46cf4f3b999d7f658853
# sudo apt install tor
# sudo apt install stem

import sys
import pickle
# import stem
# import stem.connection
# from mysql.connector import connect, Error
import time
# import urllib
# from tqdm import tqdm
# from stem import Signal
# from stem.control import Controller
# from random_user_agent.user_agent import UserAgent
# from random_user_agent.params import SoftwareName, OperatingSystem
import numpy as np
import pandas as pd
# from requests_html import HTMLSession
# from requests_html import AsyncHTMLSession
# from lxml import html
# import requests
# from lxml import etree
import re
from re import sub
# from decimal import Decimal
import datetime
# from html.parser import HTMLParser
# from bs4 import BeautifulSoup
import os
import csv
import json
# import subprocess
# import threading
import logging
# import multiprocessing
# import sqlite3
# from multiprocessing import Process, Manager, Value
# import configparser
# import unicodedata
from sklearn.linear_model import LinearRegression
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.ERROR)
logging.getLogger("imported_module").setLevel(logging.NOTSET)
print("this is utils!")

# class LineNotifications():
#     def __init__(self, token):
#         self.TOKEN = token
#         self.URL = 'https://notify-api.line.me/api/notify'
#
#     def send_text(self, str):
#         """Send a LINE Notify message (with or without an image)."""
#         headers = {'Authorization': 'Bearer ' + self.TOKEN}
#         payload = {'message': str}
#         r = requests.post(self.URL, headers=headers, params=payload)
#         print("STATUS CODE=", r.status_code)
#
#     def send_image(self, file_path):
#         """Send a LINE Notify message (with or without an image)."""
#         headers = {'Authorization': 'Bearer ' + self.TOKEN}
#         payload = {'message': "GOT IMAGE"}
#         files = {'imageFile': open(file_path, 'rb')} if file_path else None
#         print(files)
#         r = requests.post(self.URL, headers=headers, params=payload, files=files)
#         if files:
#             files['imageFile'].close()
#         print("STATUS CODE=", r.status_code)
#
# class SQLColumn():
#     def __init__(self, name, prikey, notnull, dtype):
#         self.name = name
#         self.prikey = prikey
#         self.notnull = notnull
#         self.dtype = dtype
#
#     def genform(self):
#         if self.prikey and self.notnull:
#             return '''{} {} NOT NULL PRIMARY KEY'''.format(self.name, self.dtype)
#         elif self.prikey:
#             return '''{} {} PRIMARY KEY'''.format(self.name, self.dtype)
#         elif self.notnull:
#             return '''{} {} NOT NULL'''.format(self.name, self.dtype)
#         else:
#             return '''{} {}'''.format(self.name, self.dtype)

# class MySQLColumns():
#     def __init__(self):
#         self.columns = []
#         self.prikeys = []
#
#     def append(self, name, prikey, notnull, dtype):
#         self.columns += [{"name"}:name, {"prikey"}:prikey,
#                          {"notnull"}:notnull, {"dtype"}:dtype]
#
#     def addColumnsToTable(self, DBM, table):
#         self.DBM = DBM
#         self.table
#         existings = self.DBM.getcolumsn(self.table)


# class DataBaseManager():
    # def __init__(self, dbpath):
    #     self.DBPATH = dbpath
    #     self.CN = sqlite3.connect(dbpath)
    #     self.CS = self.CN.cursor()
    #     self.execute = self.CS.execute
    #     self.executemany = self.CS.executemany
    #
    # def close(self):
    #     self.CN.commit()
    #     self.CN.close()
    #
    # def commit(self):
    #     self.CN.commit()
    #
    # # def execute(self, command):
    # #     self.CS.execute(command)
    #
    # def write(self, command, vals):
    #     self.CS.execute(command, vals)
    #
    # def genform(self, N):
    #     return '(' + '?,'*(N-1) + '?' + ')'
    #
    # def addcolumn(self, tablename, columnname, type, default=None):
    #     if columnname not in self.getcolumns(tablename):
    #         # logging.info("column {} already exists".format(columnname))
    #         self.CS.execute('''ALTER TABLE {tablename}
    #                            ADD {columnname} {type} DEFAULT {default}'''.format(tablename=tablename,
    #                                                              columnname=columnname,
    #                                                              type=type,
    #                                                              default=default))
    #     self.commit()
    #
    # # def addtable(self, table, columns, replace=False):
    # #     '''
    # #     table : table name
    # #     # columns : {"col1":["REAL", "PRIKEY", "col2":"TEXT", ...}
    # #     # columns = ["col1 TEXT PRIMARY KEY", "col2 ..]
    # #     # columns = [["col1", True, True, SQLTEXT], ["col2", False, False, SQLREAL],...]
    # #     columns = a list of SQLColumn objects
    # #     '''
    # #     if (not replace)and(table in self.gettables()):
    # #         return
    # #     if replace: self.droptable(table)
    # #     cmd = '''CREATE TABLE IF NOT EXISTS {} '''.format(table) + "("
    # #     for colid in range(len(columns)-1):
    # #         # cmd += col.genform() + ", "
    # #         cmd += columns[colid].genform() + ", "
    # #     cmd += columns[-1].genform()
    # #     cmd += " )"
    # #     print(cmd)
    # #     self.execute(cmd)
    # #     self.commit()
    #
    # def head(self, table, n=3):
    #     cols = self.getcolumns(table)
    #     collist = ""
    #     for col in cols:
    #         collist += col + ","
    #     collist = collist[:-1]
    #     data = self.read('''SELECT {} FROM {} LIMIT {}'''.format(collist, table, n))
    #     print(data)
    #
    # def addtable(self, table, columns, REPLACE=False):
    #     if (not REPLACE)and(table in self.gettables()):
    #         return
    #     if REPLACE: self.droptable(table)
    #     cmd = '''CREATE TABLE IF NOT EXISTS {} '''.format(table) + "("
    #     for colid in range(len(columns)):
    #         cmd += columns[colid].name + " " + columns[colid].dtype
    #         if columns[colid].notnull:
    #             cmd += " " + "NOT NULL"
    #         cmd += ","
    #     cmd += " PRIMARY KEY ("
    #     for colid in range(len(columns)):
    #         if columns[colid].prikey:
    #             cmd += columns[colid].name + ","
    #     cmd = cmd[:-1] + "));"
    #     print(cmd)
    #     self.execute(cmd)
    #     self.commit()
    #
    # def initialize_table(self, table, pricol, initvalues):
    #     # nonpricols = [col for col in self.getcolumns(table) if col != pricol]
    #     self.addcolumn(table, "_test", "REAL")
    #     for initval in initvalues:
    #         try:
    #             t1 = time.time()
    #             self.execute('''INSERT INTO {table}
    #                                 ("{col1}", "{col2}")
    #                                 VALUES (?, ?)'''.format(table=table, col1=pricol, col2="_test"),
    #                                 (initval, None))
    #         except sqlite3.IntegrityError:
    #             pass
    #             # self.execute('''UPDATE {} SET "{}"=? WHERE ticker)
    #             # t2 = time.time()
    #             # print('already exists!', (t2-t1)*1000)
    #     self.commit()
    #
    # def initcolumn(self, table, pricol, privals, initcol, initval=None):
    #     for prival in privals:
    #         try:
    #             self.execute('''INSERT INTO {} ("{}","{}") VALUES (?, ?)'''.format(table, pricol, initcol), (prival, initval))
    #         except sqlite3.IntegrityError:
    #             self.execute('''UPDATE {} SET "{}"=? WHERE {}=?'''.format(table, initcol, pricol,), (initval, prival))
    #
    #
    # def remove_database(self):
    #     self.close()
    #     if os.path.isfile(self.DBPATH):
    #         os.remove(self.DBPATH)
    #
    # def read(self, command):
    #     # pd.read_sql_query('''SELECT meta.ticker FROM meta''', CN).values.flatten()
    #     return pd.read_sql_query(command, self.CN) # ?
    #
    # def droptable(self, table_name):
    #     self.CS.execute('''DROP TABLE IF EXISTS %s'''%(table_name))
    #
    # def fechall(self):
    #     self.CS.fetchall()
    #
    # def gettables(self):
    #     self.CS.execute("SELECT name FROM sqlite_master WHERE type='table';")
    #     # print(self.CS.fetchall())
    #     res = self.CS.fetchall()
    #     tables = []
    #     for t in res:
    #         tables += [t[0]]
    #     return tables
    #
    # def getcolumns(self, table):
    #     res = list(map(lambda x:x[0], self.CN.execute('''SELECT * FROM {table}'''.format(table=table)).description))
    #     return res
    #
    # def getcollength(self, table, col):
    #     df = self.read('''SELECt {} FROM {}'''.format(table, col))
    #     return len(df)
    #
    # # def emptycolumn(self, table, column):
    # #     self.execute('''INSERT INTO {table}
    # #                         ("{col1}", "{col2}")
    # #                         VALUES (?, ?)'''.format(table=table, col1=pricol, col2=nonpricols[0]),
    # #                         (initval, None))
    # #     self.commit()


# class ConcurrentProcess():
# class MultithreadedDataBaseManager():
#     def __init__(self):
#         self.targets = [] # list of lists
#         self.process = None
#
#     # def settasks(self, tasks):
#     #     self.tasks = tasks
#     #
#     # def setprocess(self, func):
#     #     '''func takes a list a single argument, and returns a list of lists'''
#     #     self.process = func
#
#     def make_connections(self):
#         # self.CN = connect(host=host, user=user, password=password, database=database)
#         # self.CS = self.CN.cursor()
#         self.host = self.dbm.host
#         self.user = self.dbm.user
#         self.password = self.dbm.password
#         self.database = self.dbm.database
#         self.connections = []
#         p1 = Performance("MultithreadedDataBaseManager() Making connections")
#         for i in range(self.num_processes):
#             cn = connect(host=self.host, user=self.user,
#                          password=self.password, database=self.database)
#             cs = cn.cursor()
#             self.connections += [[cn, cs]]
#         p1.end()
#
#     def run(self, process, tasks, dbm, command, num_processes=-1, verbose=True):
#         '''returns: a list of lists
#            arguments: a list of lists
#         '''
#         # print("ConcurrentSearch:num targets
#         if num_processes == -1:
#             self.num_processes = multiprocessing.cpu_count()
#         else:
#             self.num_processes = num_processes
#         self.process = process
#         self.command = command
#         self.tasks = tasks
#         # print(command)
#         # print(tasks[0])
#         self.dbm = dbm
#         self.make_connections()
#         # print("NUMBER OF PROCESS:", self.num_processes)
#         self.VERBOSE = verbose
#         self.manager = Manager()
#         self.shared_results = self.manager.list() # the results
#         if len(self.tasks) < self.num_processes:
#             self.num_processes = 1
#         p1 = Performance("MultithreadedDataBaseManager() Spliting tasks")
#         task_chunks = split_task(self.tasks, self.num_processes)
#         p1.end()
#         # print(task_chunks[0][0])
#         # sys.exit()
#         # print("self.num_processes=", self.num_processes)
#         # print("len(tasks)=", len(tasks))
#         # print("len(task_chunks)=", len(task_chunks))
#         # print("len(self.connections)=", len(self.connections))
#         PROCESSES = []
#         progress = Value('i', 0)
#         # ave_rpms = {}
#         for i in range(self.num_processes):
#             # ave_rpms[i] = Value('f', 0)
#             # pr = multiprocessing.Process(target=self._process_handler, args=(self.process, task_chunks[i], self.shared_results, progress,))
#             pr = multiprocessing.Process(target=self.process, args=(self.connections[i], self.command, task_chunks[i],))
#             pr.start()
#             PROCESSES += [pr]
#         # watcher = multiprocessing.Process(target=self._progresswatch, args=(progress, len(self.tasks)))
#         # watcher.start()
#         for i in range(self.num_processes):
#             PROCESSES[i].join()
#             # if self.VERBOSE: print("PROCESS %d JOINED"%i)
#         # print("")
#         # print("ALL PROCESS JOINED")
#         self.QUIT = True
#         # watcher.join()
#         # return self.shared_results
#         # return self.cleaner(self.shared_results)
#
#
#     def _progresswatch(self, progress, goal):
#         BGN_TIME = time.time()
#         while progress.value < 0.98*goal:
#             elapsed = time.time() - BGN_TIME
#             time_str = format_time(elapsed)
#             rpm = 0
#             remaining_tasks = goal - progress.value
#             if (elapsed > 10)and(rpm != 0):
#                 remaining_time = format_time(60*(remaining_tasks / rpm))
#             else:
#                 remaining_time = "CALCULATING"
#             if self.VERBOSE:
#                 # print("{}".format(progress.value))
#                 # print('''%d/%d FINISHED (%.1f PERCENT) | REQUEST %.1f PM | IPCHANGE %.1f '''%(progress.value+1, goal, 100*progress.value/goal, rpm, ipchangerate.value))
#                 sys.stdout.write("\r" + '''%s | %d/%d FINISHED (%.1f PERCENT) | REMAINING %s '''%(time_str, progress.value+1, goal, 100*progress.value/goal, remaining_time))
#                 sys.stdout.flush()
#             time.sleep(0.2)


# class MultithreadedDataBaseManager():
    # def __init__(self, host, user, password, num_processes=-1, database=None):
    #     if num_processes == -1:
    #         self.num_processes = multiprocessing.cpu_count()
    #     else:
    #         self.num_processes = num_processes
    #     if database == None:
    #         self.CN = connect(host=host, user=user, password=password)
    #     else:
    #         self.CN = connect(host=host, user=user, password=password, database=database)
    #         self.CS = self.CN.cursor()
    #         self.host = host
    #         self.user = user
    #         self.password = password
    #         self.database = database
    #         self.execute = self.CS.execute
    #         self.executemany = self.CS.executemany


# class MySQLDataBaseManager():
#     def __init__(self, host, user, password, database=None):
#         if database == None:
#             self.CN = connect(host=host, user=user, password=password)
#         else:
#             self.CN = connect(host=host, user=user, password=password, database=database)
#             self.CS = self.CN.cursor()
#             self.host = host
#             self.user = user
#             self.password = password
#             self.database = database
#             self.execute = self.CS.execute
#             self.executemany = self.CS.executemany
#
#     # def executemany(sqlcommand, sqlvalues):
#
#
#     def make_database(self, name):
#         self.CS.execute('''CREATE DATABASE {}'''.format(name))
#         self.commit()
#         self.close()
#         self.CN = connect(host=host, user=user, password=password, database=database)
#         self.database = name
#
#     def close(self):
#         self.CN.commit()
#         self.CN.close()
#
#     def commit(self):
#         self.CN.commit()
#
#     def droptable(self, name):
#         self.execute('''DROP TABLE IF EXISTS {}'''.format(name))
#         self.commit()
#
#     # def insertmany(sql, vals):
#     #     self.CS.executemany()
#     #
#     # def updatemany(sql, vals):
#     #
#
#     # def execute(self, command):
#     #     self.CS.execute(command)
#
#     # def write(self, command, vals):
#     #     self.CS.execute(command, vals)
#
#     # def genform(self, N):
#     #     return '(' + '?,'*(N-1) + '?' + ')'
#
#     # def addcolumn(self, tablename, columnname, type, default=None):
#     #     if columnname not in self.getcolumns(tablename):
#     #         # logging.info("column {} already exists".format(columnname))
#     #         self.CS.execute('''ALTER TABLE {tablename}
#     #                            ADD {columnname} {type} DEFAULT {default}'''.format(tablename=tablename,
#     #                                                              columnname=columnname,
#     #                                                              type=type,
#     #                                                              default=default))
#     #     self.commit()
#
#     def addcolumn(self, tablename, columnname, dtype, overwrite=False):
#         if overwrite:
#             self.execute('''ALTER TABLE {} DROP COLUMN {}'''.format(tablename, columnname))
#         if columnname not in self.getcolumns(tablename):
#             self.execute('''ALTER TABLE {}
#                             ADD {} {}'''.format(tablename, columnname, dtype))
#             self.commit()
#             return
#         timelog("MySQLDataBaseManager():addcolumn() column already exists")
#
#     # def addtable(self, table, columns, replace=False):
#     #     '''
#     #     table : table name
#     #     # columns : {"col1":["REAL", "PRIKEY", "col2":"TEXT", ...}
#     #     # columns = ["col1 TEXT PRIMARY KEY", "col2 ..]
#     #     # columns = [["col1", True, True, SQLTEXT], ["col2", False, False, SQLREAL],...]
#     #     columns = a list of SQLColumn objects
#     #     '''
#     #     if (not replace)and(table in self.gettables()):
#     #         return
#     #     if replace: self.droptable(table)
#     #     cmd = '''CREATE TABLE IF NOT EXISTS {} '''.format(table) + "("
#     #     for colid in range(len(columns)-1):
#     #         # cmd += col.genform() + ", "
#     #         cmd += columns[colid].genform() + ", "
#     #     cmd += columns[-1].genform()
#     #     cmd += " )"
#     #     print(cmd)
#     #     self.execute(cmd)
#     #     self.commit()
#
#     def head(self, table, n=3):
#         cols = self.getcolumns(table)
#         collist = ""
#         for col in cols:
#             collist += col + ","
#         collist = collist[:-1]
#         data = self.read('''SELECT {} FROM {} LIMIT {}'''.format(collist, table, n))
#         print(data)
#
#     def addtable(self, table, columns, REPLACE=False):
#         if (not REPLACE)and(table in self.gettables()):
#             return
#         if REPLACE: self.droptable(table)
#         cmd = '''CREATE TABLE IF NOT EXISTS {} '''.format(table) + "("
#         for colid in range(len(columns)):
#             cmd += columns[colid].name + " " + columns[colid].dtype
#             if columns[colid].notnull:
#                 cmd += " " + "NOT NULL"
#             cmd += ","
#         cmd += " PRIMARY KEY ("
#         for colid in range(len(columns)):
#             if columns[colid].prikey:
#                 cmd += columns[colid].name + ","
#         cmd = cmd[:-1] + "));"
#         print(cmd)
#         self.execute(cmd)
#         self.commit()
#
#     def initialize_table(self, table, pricol, initvalues):
#         # nonpricols = [col for col in self.getcolumns(table) if col != pricol]
#         self.addcolumn(table, "_test", "REAL")
#         for initval in initvalues:
#             try:
#                 t1 = time.time()
#                 self.execute('''INSERT INTO {table}
#                                     ("{col1}", "{col2}")
#                                     VALUES (?, ?)'''.format(table=table, col1=pricol, col2="_test"),
#                                     (initval, None))
#             except sqlite3.IntegrityError:
#                 pass
#                 # self.execute('''UPDATE {} SET "{}"=? WHERE ticker)
#                 # t2 = time.time()
#                 # print('already exists!', (t2-t1)*1000)
#         self.commit()
#
#     def initcolumn(self, table, pricol, privals, initcol, initval=None):
#         for prival in privals:
#             try:
#                 self.execute('''INSERT INTO {} ("{}","{}") VALUES (?, ?)'''.format(table, pricol, initcol), (prival, initval))
#             except sqlite3.IntegrityError:
#                 self.execute('''UPDATE {} SET "{}"=? WHERE {}=?'''.format(table, initcol, pricol,), (initval, prival))
#
#
#     def remove_database(self):
#         self.close()
#         if os.path.isfile(self.DBPATH):
#             os.remove(self.DBPATH)
#
#     def read(self, command):
#         # pd.read_sql_query('''SELECT meta.ticker FROM meta''', CN).values.flatten()
#         # return pd.read_sql_query(command, self.CN) # ?
#         return pd.read_sql(command, con=self.CN)
#
#     def droptable(self, table_name):
#         self.CS.execute('''DROP TABLE IF EXISTS %s'''%(table_name))
#
#     def fechall(self):
#         self.CS.fetchall()
#
#     def gettables(self):
#         # self.CS.execute("SELECT name FROM sqlite_master WHERE type='table';")
#         # print(self.CS.fetchall())
#         res = self.CS.fetchall()
#         tables = []
#         for t in res:
#             tables += [t[0]]
#         return tables
#
#     # def getcolumns(self, table):
#     #     # print(self.CS.description)
#     #     # self.execute('''SELECT COLUMN_NAME FROM {}'''.format(table))
#     #     print(self.CS.column_names)
#     #     num_fields = len(self.CS.description)
#     #     field_names = [i[0] for i in self.CS.description]
#     #     print(field_names)
#     #     res = list(map(lambda x:x[0], self.CN.execute('''SELECT * FROM {table}'''.format(table=table)).description))
#     #     return res
#     def getcolumns(self, table):
#         sqlcommand = '''SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME="{}"'''.format(table)
#         self.CS.execute(sqlcommand)
#         _res = self.CS.fetchall()
#         colnames = [c[0] for c in _res]
#         return colnames
#
#     def getcollength(self, table, col):
#         df = self.read('''SELECt {} FROM {}'''.format(table, col))
#         return len(df)

# class ConcurrentProcess():
#     def __init__(self):
#         self.targets = [] # list of lists
#         self.process = None
#
#     def settasks(self, tasks):
#         self.tasks = tasks
#
#     def setprocess(self, func):
#         '''func takes a list a single argument, and returns a list of lists'''
#         self.process = func
#
#     def run(self, num_processes=-1, verbose=True,
#             none2null=True, removeempty=True, sharedargs=None):
#         '''returns: a list of lists
#            arguments: a list of lists
#         '''
#         # print("ConcurrentSearch:num targets
#         if num_processes == -1:
#             self.num_processes = multiprocessing.cpu_count()
#         else:
#             self.num_processes = num_processes
#         # print("NUMBER OF PROCESS:", self.num_processes)
#         self.VERBOSE = verbose
#         self.none2null = none2null
#         self.manager = Manager()
#         self.shared_results = self.manager.list() # the results
#         if len(self.tasks) < self.num_processes:
#             self.num_processes = 1
#
#         if self.num_processes == 1:
#             upw = universalProgressWatcher("ConcurrentProcess()", len(self.tasks))
#             upw.start()
#             allres = []
#             for task, index in forEach(self.tasks):
#                 if sharedargs == None:
#                     res = self.process(task)
#                 else:
#                     res = self.process(task, sharedargs)
#                 if res != None:
#                     if self.none2null: allres += self.clean(res)
#                     else: allres += res
#                 upw.progress.value += 1
#             upw.end()
#             return allres
#         if self.num_processes > 1:
#             p1 = Performance("[+] ConcurrentProcess() spliting tasks")
#             task_chunks = split_task(self.tasks, self.num_processes)
#             p1.end()
#             PROCESSES = []
#             progress = Value('i', 0)
#             # ave_rpms = {}
#             upw = universalProgressWatcher("ConcurrentProcess()", len(self.tasks))
#             upw.start()
#             for i in range(self.num_processes):
#                 pr = multiprocessing.Process(target=self._process_handler, args=(self.process, task_chunks[i], self.shared_results, upw.progress,sharedargs))
#                 pr.start()
#                 PROCESSES += [pr]
#             # watcher = multiprocessing.Process(target=self._progresswatch, args=(progress, len(self.tasks)))
#             # watcher.start()
#             # print("")
#
#             for i in range(self.num_processes):
#                 PROCESSES[i].join()
#                 # if self.VERBOSE: print("PROCESS %d JOINED"%i)
#             # print("")
#             # print("ALL PROCESS JOINED")
#             self.QUIT = True
#             upw.end()
#             # watcher.join()
#             return self.shared_results
#         # return self.cleaner(self.shared_results)
#
#     # single mode
#     def _process_handler(self, process, tasks, shared_results, progress, sharedargs):
#         for task in tasks:
#             if sharedargs == None:
#                 res = process(task)
#             else:
#                 res = process(task, sharedargs)
#             if res != None:
#                 if self.none2null: shared_results += self.clean(res)
#                 else: shared_results += res
#             progress.value += 1
#
#     # # multi mode # progress watch won't work
#     # def _process_handler_multimode(self, process, tasks, shared_results, progress):
#     #     res = procees(tasks)
#     #     res_cleansed = []
#     #
#     #     for r in res:
#     #         # progress.value += 1
#     #         if res == None: continue
#     #         if self.none2null: shared_results += self.clean(res)
#     #         else: shared_results += res
#
#     def clean(self, res):
#         # print("res=", res)
#         nrows = len(res)
#         ncols = len(res[0])
#         for r in range(nrows):
#             for c in range(ncols):
#                 if (res[r][c] == None)or(res[r][c] == ""):
#                     res[r][c] = "NULL"
#         return res
#
#     def _progresswatch(self, progress, goal):
#         BGN_TIME = time.time()
#         while progress.value < 0.98*goal:
#             elapsed = time.time() - BGN_TIME
#             time_str = format_time(elapsed)
#             rpm = 0
#             remaining_tasks = goal - progress.value
#             if (elapsed > 10)and(rpm != 0):
#                 remaining_time = format_time(60*(remaining_tasks / rpm))
#             else:
#                 remaining_time = "CALCULATING"
#             if self.VERBOSE:
#                 # print("{}".format(progress.value))
#                 # print('''%d/%d FINISHED (%.1f PERCENT) | REQUEST %.1f PM | IPCHANGE %.1f '''%(progress.value+1, goal, 100*progress.value/goal, rpm, ipchangerate.value))
#                 sys.stdout.write("\r" + '''%s | %d/%d FINISHED (%.1f PERCENT) | REMAINING %s '''%(time_str, progress.value+1, goal, 100*progress.value/goal, remaining_time))
#                 sys.stdout.flush()
#             time.sleep(0.05)
#         sys.stdout.write("\r" + '''%s | %d/%d FINISHED (%.1f PERCENT) | REMAINING %s '''%(time_str, goal, goal, 100, remaining_time))
#         sys.stdout.flush()
#         print("")

# class FastAggregate():
#     def __init__(self):
#         pass
#
#     def run(self, tasks, targetindex, num_processes=-1, removeempty=False):
#         self.tasks = tasks
#         self.targetindex = targetindex
#         if num_processes == -1:
#             self.num_processes = multiprocessing.cpu_count()
#         else:
#             self.num_processes = num_processes
#         # self.shared_results = self.manager.list()
#         if len(self.tasks) < self.num_processes:
#             self.num_processes = 1
#         p1 = Performance("[+] FastAggregate() splitting tasks. len(tasks)={}".format(len(self.tasks)))
#         task_chunks = split_task(self.tasks, self.num_processes)
#         p1.end()
#         manager = Manager()
#         shvr = manager.dict()
#         shls = manager.list()
#         # progress = Value('i', 0)
#         upw = universalProgressWatcher("FastAggregate()", len(self.tasks))
#         shvr["exit"] = False
#         shvr["targetindex"] = targetindex
#         shvr["removeempty"] = removeempty
#         # shvr["progress"] = [0]*self.num_processes
#         processes = []
#         upw.start()
#         for i in range(self.num_processes):
#             p = multiprocessing.Process(target=self._aggregate, args=(task_chunks[i], shls, shvr, upw.progress))
#             p.start()
#             processes += [p]
#         for i in range(self.num_processes):
#             processes[i].join()
#         # print(shvr)
#         upw.end()
#         agg = self.postprocess(shls)
#         return agg
#
#     def postprocess(self, shls):
#         p1 = Performance("[+] FastAggregate() start postprocess")
#         agg = {}
#         for entry in shls:
#             # print(entry)
#             key, agglist = entry
#             if key not in agg.keys():
#                 agg[key] = agglist
#             else:
#                 agg[key] += agglist
#         p1.end()
#         return agg
#
#     def _aggregate(self, taskchunk, shls, shvr, progress):
#         agg = {}
#         targetindex = shvr["targetindex"]
#         for task in taskchunk:
#             # print(task)
#             if (shvr["removeempty"])and(anyempty(task)): continue
#             if task[targetindex] not in agg.keys():
#                 agg[task[targetindex]] = [task]
#             else:
#                 agg[task[targetindex]] += [task]
#             progress.value += 1
#         # print(agg)
#         res = []
#         for key in agg.keys():
#             # agg[key]
#             res += [[key, agg[key]]]
#         # print(res)
#         shls += res




# class ConcurrentSearch():
#     def __init__(self):
#         self.ACQUIRED = False
#         self.QUIT = False
#         self.search_targets = {}
#         self.tasks = {}
#         self.target_names = {}
#         self.targets = {}
#
#     # def add_target(self, order, name, pattern, dtype, n):
#     def add_target(self, order, name, dtype, n, pattern):
#         # self.num_targets += 1
#         self.target_names[order] = name
#         # self.search_targets[order] = Pattern(n, dtype, pattern)
#         self.search_targets[order] = Pattern(pattern, n, dtype)
#         self.targets[name] = [n, dtype, pattern]
#
#
#     def add_task(self, index, filepath):
#         if index not in self.tasks.keys():
#             self.tasks[index] = filepath
#
#     def run(self, num_processes=1, max_rpm=60, verbose=False,
#             none2null=True, process=None):
#         '''returns:
#            1. a list that containes the propertie names
#            2. a list of lists containing the search results
#            [["index", "market-cap", "prev-close"]
#             [["AAPL", 4093.4, 9924.2], ...]]
#            arguments:
#         '''
#         print("ConcurrentSearch:Start")
#         if process != None:
#             # when a specific function is given
#             pass
#
#         if num_processes == -1:
#             self.num_processes = multiprocessing.cpu_count()
#         else:
#             self.num_processes = num_processes
#         print("ConcurrentSearch:Num Processes=", self.num_processes)
#         self.max_rpm = max_rpm
#         self.VERBOSE = verbose
#         self.none2null = none2null
#         self.manager = Manager()
#         self.shared_results = self.manager.list() # the results
#         self.search_targets = dict(sorted(self.search_targets.items()))
#         if len(self.tasks) < self.num_processes:
#             # self.QUIT = True
#             # sys.exit("ERROR:number of jobs must be greater than number of subprocess")
#             self.num_processes = 1
#         # tasks_chunks = self._split_task(self.tasks, self.num_processes)
#         tasks_chunks = split_task(self.tasks, self.num_processes)
#         # print("tasks_chunks:", tasks_chunks)
#         PROCESSES = []
#         progress = Value('i', 0)
#         # ave_rpms = {}
#         for i in range(self.num_processes):
#             # ave_rpms[i] = Value('f', 0)
#             pr = multiprocessing.Process(target=self._process, args=(self.search_targets, tasks_chunks[i], self.shared_results, progress,))
#             pr.start()
#             PROCESSES += [pr]
#         print("ConcurrentSearch:All Processes Started")
#         watcher = multiprocessing.Process(target=self._progresswatch, args=(progress, len(self.tasks)))
#         watcher.start()
#         for i in range(self.num_processes):
#             PROCESSES[i].join()
#             # if self.VERBOSE: print("PROCESS %d JOINED"%i)
#         watcher.join()
#         print("ConcurrentSearch:All Processes Joined")
#         self.QUIT = True
#         return self.reshandler(self.shared_results)
#
#         # return self.shared_results
#
#
#     def reshandler(self, sres):
#         names = list(dict(sorted(self.target_names.items())).values())
#         names = ["id"] + names
#         dres = []
#         for res in sres:
#             nres = {}
#             # if res[0] == "RDS.A":
#             #     print("res={}".format(res))
#             #     print("names={}".format(names))
#             for name, val in zip(names, res):
#                 if ((val == None)or(val == ''))and(self.none2null):
#                     val = "NULL"
#                 nres[name] = val
#             # for name in names:
#             #     val = res[name]
#             #     if (va == None)and(self.none2null):
#             #         val = "NULL"
#             #     nres = val
#             dres += [nres]
#         return dres
#
#     def _process(self, search_targets, tasks, shared_results, progress):
#         '''this function works as another system process'''
#         for task_id in tasks: # path to the target file to search
#             res = [task_id]
#             filepath = tasks[task_id]
#             str = readfile(filepath)
#             if str == None:
#                 res += [None]*len(search_targets)
#             else:
#                 for target_id in search_targets: # targets are already sorted
#                     val = search_targets[target_id].findone(str)[0]
#
#                     # print("val:", val)
#                     res += [val]
#             shared_results += [res]
#             progress.value += 1
#
#     def _run_processes(self):
#         if len(self.all_tasks) < self.num_processes:
#             # self.QUIT = True
#             # sys.exit("ERROR:number of jobs must be greater than number of subprocess")
#             self.num_processes = 1
#
#         tasks_split = self._split_task(self.all_tasks, self.num_processes)
#         PROCESSES = []
#         progress = Value('i', 0)
#         # ave_rpms = {}
#         for i in range(self.num_processes):
#             # ave_rpms[i] = Value('f', 0)
#             pr = multiprocessing.Process(target=self._process, args=(self.target_func, tasks_split[i], self.shared_results, progress,))
#             pr.start()
#             PROCESSES += [pr]
#         print("ConcurrentSearch:All Process Started")
#         # watcher = multiprocessing.Process(target=self._progresswatch, args=(progress,len(jobs),self.ipchangerate, ave_rpms,))
#         # watcher.start()
#         for i in range(self.num_processes):
#             PROCESSES[i].join()
#             # if self.VERBOSE: print("PROCESS %d JOINED"%i)
#         watcher.join()
#         print("")
#         print("ConcurrentSearch:All Processes Joined")
#         self.QUIT = True
#
#     def _progresswatch(self, progress, goal):
#         BGN_TIME = time.time()
#         name = "ConcurrentSearch"
#         while progress.value < 0.98*goal:
#             elapsed = time.time() - BGN_TIME
#             time_str = format_time(elapsed)
#             rpm = 0
#             remaining_tasks = goal - progress.value
#             if (elapsed > 10)and(rpm != 0):
#                 remaining_time = format_time(60*(remaining_tasks / rpm))
#             else:
#                 remaining_time = "CALCULATING"
#             if self.VERBOSE:
#                 # print("{}".format(progress.value))
#                 # print('''%d/%d FINISHED (%.1f PERCENT) | REQUEST %.1f PM | IPCHANGE %.1f '''%(progress.value+1, goal, 100*progress.value/goal, rpm, ipchangerate.value))
#                 sys.stdout.write("\r" + name + ''' | %s | %d/%d (%.1f percent) finished | remaining %s '''%(time_str, progress.value+1, goal, 100*progress.value/goal, remaining_time))
#                 sys.stdout.flush()
#             time.sleep(0.05)
#         sys.stdout.write("\r" + name + ''' | %s | %d/%d (%.1f percent) finished | remaining %s '''%(time_str, goal, goal, 100, remaining_time))
#         sys.stdout.flush()
#         print("")

# class AnonymizedConcurrentRequest():
#     def __init__(self, tor_password, proxies, control_port=9051, max_rpm=45, ipchange_interval=1,
#                  num_processes=1, overwrite=True, verbose=False):
#         self.TOR_PASSWORD = tor_password
#         self.IP_CHECK_SERVICE = "http://icanhazip.com/"
#         self.IP_CHECK_INTERVAL = ipchange_interval # sec
#         if num_processes == -1:
#             self.n = multiprocessing.cpu_count()
#         else:
#             self.n = num_processes
#         self.overwrite = overwrite
#         self.oldIP = "0.0.0.0"
#         self.newIP = "0.0.0.0"
#         self.oldIP_save = "0.0.0.0"
#         self.VERBOSE=verbose
#         self.PROXIES = proxies
#         self.CONTROL_PORT = control_port
#         self.ipchange_interval = ipchange_interval
#         self.ipchangerate = Value('f', 0)
#         self.ipchagetime = None
#         self.max_rpm = max_rpm # 30 request per minute
#         self.last_update = time.time()
#         self.last_request = time.time()
#         self.ACQUIRED = False
#         self.QUIT = False
#         self.proxyset_time = None
#         self.request_time = None
#         software_names = [SoftwareName.CHROME.value]
#         operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
#         self.user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
#         # self._ip_changer(interval=ipchange_interval)
#
#     def _ip_changer(self):
#         self.ipcprocess = threading.Thread(target=self._ipchanger_thread,
#                                args=(self.ipchange_interval, self.ipchangerate,self.exitflag,))
#         self.ipcprocess.start()
#         # th1.join()
#         # print("IP CHANGER JOINED")
#
#     def _ipchanger_thread(self, interval, ipchangerate, exitflag):
#         while True:
#             if self.QUIT: break
#             if exitflag.value == 1: break
#             with Controller.from_port(port = self.CONTROL_PORT) as controller:
#                 controller.authenticate(password = self.TOR_PASSWORD)
#                 controller.signal(Signal.NEWNYM)
#                 controller.close()
#             self.newIP = self._request(self.IP_CHECK_SERVICE)
#             time.sleep(interval)
#             if self.newIP != self.oldIP:
#                 self.oldIP = self.newIP
#                 # print("New IP:", self.newIP)
#                 # print("NEW IP:", self.newIP.decode("utf-8").replace("\n", ""))
#                 et = time.time() - self.last_update
#                 self.last_update = time.time()
#                 ipchangerate.value = 60.0/(et)
#                 # print("ipchangerate:%.1f"%ipchangerate.value)
#
#     def _request(self, url):
#         t1s = time.time()
#         _proxy_support = urllib.request.ProxyHandler(self.PROXIES)
#         _opener = urllib.request.build_opener(_proxy_support)
#         urllib.request.install_opener(_opener)
#         t1e = time.time()
#         user_agent = self.user_agent_rotator.get_random_user_agent()
#         headers={'User-Agent':user_agent}
#         t2s = time.time()
#         try:
#             request=urllib.request.Request(url, None, headers)
#             result = urllib.request.urlopen(request).read()
#         except (urllib.error.HTTPError, urllib.error.URLError) as e:
#             # print(str(e))
#             return 'ERROR'
#         t2e = time.time()
#         self.proxyset_time = t1e - t1s
#         self.request_time = t2e - t2s
#         return result.decode("utf-8")
#
#     def run(self, jobs):
#         if not self.overwrite:
#             jobs = self.selectjobs(jobs)
#             # print(jobs)
#         if len(jobs) <= self.n:
#             self.n = 1
#         self.max_rpm_per_thread = self.max_rpm*1.0/self.n
#         jobs_split = split_task(jobs, self.n)
#         THREADS = []
#         progress = Value('i', 0)
#         self.exitflag = Value('i', 0)
#         self._ip_changer()
#         ave_rpms = {}
#         for i in range(self.n):
#             ave_rpms[i] = Value('f', 0)
#             pr = multiprocessing.Process(target=self._request_thread, args=(jobs_split[i], progress, ave_rpms[i],))
#             pr.start()
#             # time.sleep(1)
#             THREADS += [pr]
#         watcher = multiprocessing.Process(target=self._progresswatch, args=(progress,len(jobs),self.ipchangerate, ave_rpms,self.exitflag,))
#         watcher.start()
#         for i in range(self.n):
#             THREADS[i].join()
#             # if self.VERBOSE: print("PROCESS %d JOINED"%i)
#         self.exitflag.value = 1
#         self.QUIT = True
#         watcher.join()
#         self.ipcprocess.join()
#
#     def selectjobs(self, jobs):
#         selected_jobs = []
#         for filepath, url in jobs:
#             if os.path.exists(filepath):
#                 continue
#             else:
#                 selected_jobs += [[filepath, url]]
#         return selected_jobs
#
#     def _progresswatch(self, progress, goal, ipchangerate, ave_rpms, exitflag):
#         vn2 = progress.value
#         BGN_TIME = time.time()
#         # while progress.value < 0.99*goal:
#         while True:
#             if exitflag.value == 1:
#                 break
#             elapsed = time.time() - BGN_TIME
#             time_str = format_time(elapsed)
#             rpm = 0
#             for i in range(len(ave_rpms)):
#                 rpm += ave_rpms[i].value
#             remaining_tasks = goal - progress.value
#             if (elapsed > 10)and(rpm != 0):
#                 remaining_time = format_time(60*(remaining_tasks / rpm))
#             else:
#                 remaining_time = "CALCULATING"
#             if self.VERBOSE:
#                 try:
#                     progress_percent = 100*progress.value/goal
#                 except:
#                     progress_percent = -1
#                 sent = '''\r''' + gettime(color=bcolors.OKCYAN) + " " + '''%d/%d (%.1f percent) - %.1f requests/min - remaining %s - %.1f ipchage/min'''%(progress.value+1, goal, progress_percent, rpm, remaining_time, ipchangerate.value)
#                 sys.stdout.write(sent)
#                 sys.stdout.flush()
#             time.sleep(0.05)
#
#     def _request_thread(self, jobs, progress, ave_rpm):
#         last_request = time.time()
#         ave_rpm.value = 0
#         for job in jobs:
#             t1s = time.time()
#             t2s = time.time()
#             SAVE_PATH = job[0]
#             if os.path.exists(SAVE_PATH) and (not self.overwrite):continue
#             URL = job[1]
#             html = self._request(URL)
#             progress.value += 1
#             if html == "ERROR":
#                 continue
#             with open(SAVE_PATH, "w") as f:
#                 f.write(html)
#             et2 = time.time() - t2s
#             # last_request = time.time()
#             sleeptime = 60./self.max_rpm_per_thread - et2
#             # print("sleeptime:", sleeptime)
#             # print(sleeptime, self.max_rpm_per_thread, et2)
#             if sleeptime > 0:
#                 time.sleep(sleeptime)
#             t1e = time.time()
#             ave_rpm.value = 1.0*60.0/(t1e - t1s)
#         ave_rpm.value = 0

# class Pattern():
#     def __init__(self, pattern, n=None, dtype=None):
#         self.n = n
#         self.dtype = dtype
#         self.pattern = pattern
#         self.compiled = re.compile(str2raw(self.pattern))
#
#
#     def find(self, str):
#         res = self.compiled.findall(str)
#         return res
#
#     def findall(self, str):
#         return self.compiled.finditer(str)
#         # return [[start, end,
#
#     def findone(self, str):
#         # cmp = re.compile(str2raw(pattern))
#         # res = cmp.findall(str)
#         res = self.find(str)
#         if len(res) == 0:
#             return [None]
#         else:
#             # print("self.n", self.n)
#             val = res[0][self.n]
#             if (val != "")and(self.dtype != "string"):
#                 val = str2num(val, self.dtype)
#             return [val]

# class Regex():
#     def __init__(self, pattern):
#         self.pattern = pattern
#         self.compiled = re.compile(str2raw(self.pattern))
#
#     def findall(text):
#         self.foundres = self.cmpiled.findall(test)

#
# class AnonymizedRequest():
#     def __init__(self, password):
#         self.TOR_PASSWORD = password
#         self.IP_CHECK_SERVICE = "http://icanhazip.com/"
#         self.IP_CHECK_INTERVAL = 1 # sec
#         self.oldIP = "0.0.0.0"
#         self.newIP = "0.0.0.0"
#         self.oldIP_save = "0.0.0.0"
#         self.ipchangerate = 60 # chage ip at least onece in 60 secs
#         self.ipchagetime = None
#         self.max_rmp = 45 # 30 request per minute
#         self.last_update = time.time()
#         self.last_request = time.time()
#         self.ACQUIRED = False
#         self.QUIT = False
#         self.proxyset_time = None
#         self.request_time = None
#         software_names = [SoftwareName.CHROME.value]
#         operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
#         self.user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
#         self.ln = LineNotifications("eYAphLEuy58SyPFyCXv3b51jlGo8UoetWwXPTfPSaHV")
#
#     def random_sleep(self, ll, ul):
#         # in milli seconds
#         t = np.random.uniform(ll, ul)
#         time.sleep(t)
#
#     def _request(self, url):
#         # communicate with TOR via a local proxy (privoxy)
#         def _set_urlproxy():
#             proxy_support = urllib.request.ProxyHandler({"http" : "127.0.0.1:8118"})
#             opener = urllib.request.build_opener(proxy_support)
#             urllib.request.install_opener(opener)
#         t1s = time.time()
#         _set_urlproxy()
#         t1e = time.time()
#         user_agent = self.user_agent_rotator.get_random_user_agent()
#         headers={'User-Agent':user_agent}
#         t2s = time.time()
#         try:
#             request=urllib.request.Request(url, None, headers)
#             result = urllib.request.urlopen(request).read()
#         except (urllib.error.HTTPError, urllib.error.URLError) as e:
#             # self.ln.send_text("[ERROR] " + str(e))
#             # self.QUIT = True
#             # quit()
#             return b'ERROR'
#         t2e = time.time()
#         self.proxyset_time = t1e - t1s
#         self.request_time = t2e - t2s
#         return result
#
#     def renew_connection(self):
#         self.oldIP = self.newIP
#         with Controller.from_port(port = 9051) as controller:
#             controller.authenticate(password = self.TOR_PASSWORD)
#             controller.signal(Signal.NEWNYM)
#             controller.close()
#
#         while self.oldIP == self.newIP:
#             time.sleep(self.IP_CHECK_INTERVAL)
#             self.newIP = self._request(self.IP_CHECK_SERVICE)
#         print("NEW IP:", self.newIP)
#
#     def _ipchanger_thread(self, interval):
#         while True:
#             if self.QUIT:quit()
#             self.oldIP = self.newIP
#             with Controller.from_port(port = 9051) as controller:
#                 controller.authenticate(password = self.TOR_PASSWORD)
#                 controller.signal(Signal.NEWNYM)
#                 controller.close()
#             self.newIP = self._request(self.IP_CHECK_SERVICE)
#             time.sleep(interval)
#             if self.newIP != self.oldIP:
#                 print("NEW IP:", self.newIP.decode("utf-8").replace("\n", ""))
#                 # self.ipchagetime = time.time()
#
#
#     def renew_connection_always(self, interval):
#         th1 = threading.Thread(target=self._ipchanger_thread,
#                                args=(interval,))
#         th1.start()
#
#     def _wait_acquisition(self):
#         while self.ACQUIRED:
#             time.sleep(0.01)
#         self.ACQUIRED = True
#
#     def _wait_ipchage(self):
#         while True:
#             if self.oldIP != self.newIP:
#                 self.oldIP_save = self.newIP
#                 self.last_update = time.time()
#                 break
#
#     def request(self, url):
#         # self.oldIP_save =
#         t1s = time.time()
#         if t1s - self.last_request < 60./self.max_rmp:
#             time.sleep(60./self.max_rmp - (t1s - self.last_request))
#             # print("sleep")
#         self.rmp = 60./(time.time() - self.last_request)
#         self.last_request = time.time()
#         if self.oldIP_save != self.newIP:
#             self.oldIP_save = self.newIP
#             self.last_update = time.time()
#         else:
#             if time.time() - self.last_update > self.ipchangerate:
#                 # print("SAME IP FOR OVER %d SECS"%(int(self.last_update)))
#                 self._wait_ipchage()
#                 # self.ln.send_text("[ERROR] SAME IP FOR 120 SECS")
#                 # quit()
#         # self._wait_acquisition()
#         if self.newIP == "0.0.0.0":
#             self.renew_connection()
#         result = self._request(url)
#         # self.last_request = time.time()
#         print("IP:%s, RMP:%d, SET PROXY:%d ms, REQUEST:%d ms, URL:%s"%(self.newIP.decode("utf-8").replace('\n', ''), int(self.rmp), int(self.proxyset_time*1e3), int(self.request_time*1e3), url))
#         return result

def split_task(jobs, n):
    # print(jobs[:5])
    # print(n)
    spl = []
    N = len(jobs)
    # print(type(jobs))
    if (isinstance(jobs, list))or(isinstance(jobs, multiprocessing.managers.ListProxy)):
    # if (isinstance(jobs, list)):
        for i in range(n):
            try:
                spl += [jobs[int(i*N/n):int((i+1)*N/n)]]
            except:
                print("except:", i, n, N )
        return spl
    elif isinstance(jobs, dict):
        # print("dict:{d}".format(d=dict))
        keys = list(jobs.keys())
        # print("keys:{keys}".format(keys=keys))
        keys_split = split_task(keys, n)
        # print("keys_split:{sp}".format(sp=keys_split))
        for i in range(n):
            d = {}
            for key in keys_split[i]:
                d[key] = jobs[key]
            spl += [d]
        return spl

def isempty(val):
    if (val==None)or(val=="NULL")or(val=="")or(val=="None"): return True
    else:
        try:
            return np.isnan(val)
        except:
            pass
    return False

def anyempty(vals):
    N = len(vals)
    for n in range(N):
        if isempty(vals[n]): return True
    return False

def ifEmptyThenNone(val):
    if (isinstance(val, list))or(isinstance(val, np.ndarray)):
        res = []
        for i in range(len(val)):
            if isempty(val[i]):
                res += [None]
            else:
                res += [val[i]]
        return res
    else:
        if isempty(val): return None
        return val

# def isListOrNumpy(vals):


def allempty(vals):
    N = len(vals)
    res = True
    for n in range(N):
        # if isempty(vals[n]): res *=
        res *= isempty(vals[n])
    return res


def save_as_json(dict, name):
    with open(name + '.json', 'w') as fp:
        json.dump(dict, fp)

def load_from_json(name):
    with open(name + '.json', 'r') as fp:
        data = json.load(fp)
    return data

def list2pickle(list, path):
    with open(path, "wb") as f:
        pickle.dump(list, f)

def pickle2list(path):
    with open(path, "rb") as f:
        return pickle.load(f)

def list2csv(list, path):
    # with open(path, "w") as f:
    #     write = csv.writer(f)
    #     write.writerow(list)
    pd.DataFrame({"data":list}).to_csv(path, header=None)

def csv2list(path):
    # with open(path, newline='') as f:
    #     reader = csv.reader(f)
    #     data = list(reader)
    #     res = [r[0] for r in data]
    #     return res
    return list(pd.read_csv(path, header=None).values[:,1])

def ifExistsRemove(path):
    if os.path.exists(path):
        os.remove(path)

def str2raw(str):
    return r'{}'.format(str)

def find(pattern, str):
    # cmp = re.compile(r'(<td style="text-align:center">)(\d\d\d\d)(</td>)')
    cmp = re.compile(str2raw(pattern))
    res = cmp.findall(str)
    return res

def findone(str, idx, dtype, pattern):
    cmp = re.compile(str2raw(pattern))
    res = cmp.findall(str)
    if len(res) == 0:
        return [None]
    else:
        val = res[0][idx]
        if dtype == "float":
            val = float(val)
        elif dtype == "int":
            val = int(val)
        elif dtype == "string":
            pass
        return [val]

def securemul(val1, val2):
    if (val1 == None)or(val2 == None):return None
    elif (val1 == "NULL")or(val2 == "NULL"):return None
    else: return val1*val2



def str2num(str, type):
    if (str == "")or(str == None): return None
    UNITS = {"K":1e3, "M":1e6, "B":1e9, "T":1e12}
    MUL = 1
    for u in UNITS:
        if u in str:
            str = str[:-1]
            MUL = UNITS[u]

    if type == "int":
        str = str.replace(",", "")
        val = int(int(str)*MUL)
    elif type == "float":
        str = str.replace(",", "")
        val = float(str)*MUL
    return val

def cunit2vunit(str):
    if str == "K":return 1e3
    elif str == "M":return 1e6
    elif str == "B":return 1e9
    elif str == "T":return 1e12
    else: sys.exit("no match found")

def readfile(filepath):
    try:
        with open(filepath) as f:
            return f.read()
    except FileNotFoundError:
        # return [index, None, None]
        return None

def writefile(text, filepath):
    file = open(filepath, "w")
    n = file.write(text)
    file.close()

def format_time(sec):
    H = int(sec/(60*60))
    M = int((sec - H*60*60)/60)
    S = int((sec - H*60*60 - M*60))
    return "{:02d}".format(H) +":"+ "{:02d}".format(M) + ":" + "{:02d}".format(S)

def str2dtime(str):
    # if isinstance(str, np.ndarray):
    #     str = list(str)
    if isArrayLike(str):
        str = arraylikeToList(str)
        res = []
        for i in range(len(str)):
            res += [str2dtime(str[i])]
        return res
    try:
        return datetime.datetime.strptime(str, '%Y-%m-%d')
    except:
        return datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S')

def stringToDatetime(str):
    if isArrayLike(str):
        return str2dtime(str) # list
    else:
        return str2dtime(str)



def isList(x):
    if isinstance(x, list): return True
    return False
def isNdarray(x):
    if isinstance(x, np.ndarray): return True
    return False
def isSeries(x):
    if isinstance(x, pd.core.series.Series): return True
    return False
def isArrayLike(values):
    if isList(values): return True
    if isNdarray(values): return True
    if isSeries(values): return True
    return False
def arraylikeToList(values):
    if isList(values):
        return values
    if isNdarray(values) or isSeries(values):
        return list(values)
    return None
def arraylikeToNdarray(values):
    if isList(values):
        return np.array(values)
    if isNdarray(values) or isSeries(values):
        return np.array(values)
    return None


# class universalProgressWatcher():
#     def __init__(self, name, N):
#         self.name = name
#         self.N = N
#         self.progress = Value('i', 0)
#         self.quit = Value('i', 0)
#
#     def start(self):
#         self.p = multiprocessing.Process(target=self._watcher, args=(self.name, self.N, self.progress, self.quit))
#         self.p.start()
#
#     def end(self):
#         self.quit.value = 1
#         time.sleep(300e-3)
#         self.p.join()
#
#     def _watcher(self, name, N, progress, quit):
#         BGN_TIME = time.time()
#         fps = 0
#         elapsed = 0
#         SMOOTHING = 0.999
#         lasttime = time.time()
#         print(gettime(color=bcolors.OKCYAN) + " " + "Start Progress Watcher: " + name)
#         progress_last = 0
#         count = 0
#         while True:
#             count += 1
#             time.sleep(100e-3)
#             progress_now = progress.value
#             dProgress = progress_now - progress_last
#             progress_last = progress_now
#             timestep = time.time() - lasttime
#             lasttime = time.time()
#             if count == 1: continue # first iteration cannot be trusted
#             fps = (1-SMOOTHING)*fps + SMOOTHING*(dProgress)/timestep
#             elapsed = time.time() - BGN_TIME
#             time_str = format_time(elapsed)
#             remaining_tasks = N - progress_now
#             if fps < 1: fps = 1
#             remaining_time = format_time(remaining_tasks/fps)
#             sent = '''\r''' + gettime(color=bcolors.OKCYAN) + " " + '''%d/%d (%.1f percent) finished - %.1f iters/sec - remaining %s '''%(progress_now+1, N, 100*progress_now/N, fps, remaining_time)
#             sys.stdout.write(sent)
#             sys.stdout.flush()
#             if quit.value == 1: break
#         sent = '''\r''' + gettime(color=bcolors.OKCYAN) + " " + '''%d/%d (%.1f percent) finished - %.1f iters/sec - remaining %s '''%(N, N, 100, fps, remaining_time)
#         sys.stdout.write(sent)
#         sys.stdout.flush()
#         print("")


# def progressbar(name, vals):
#     N = len(vals)
#     i = 0
#     BGN_TIME = time.time()
#     PRECISION = 1000
#     flushtiming = (np.arange(PRECISION)*N/PRECISION).astype(int)
#     fps = 0
#     elapsed = 0
#     SMOOTHING = 0.999
#     lasttime = time.time()
#     print(gettime(color=bcolors.OKCYAN) + " " + "Start Iteration: " + name)
#     if isinstance(vals, dict):
#         keys = list(vals.keys())
#     while True:
#         if i == N: break
#         if isinstance(vals, dict):
#             yield keys[i]
#         else:
#             yield vals[i]
#         i += 1
#         if i in flushtiming:
#             timestep = time.time() - lasttime
#             lasttime = time.time()
#             fps = (1-SMOOTHING)*fps + SMOOTHING*(flushtiming[1] - flushtiming[0])/timestep
#             elapsed = time.time() - BGN_TIME
#             time_str = format_time(elapsed)
#             remaining_tasks = N - i
#             # print("fps:", fps)
#             if fps < 1: fps = 1
#             remaining_time = format_time(remaining_tasks/fps)
#             sent = '''\r''' + gettime(color=bcolors.OKCYAN) + " " +  '''%d/%d (%.1f percent) finished - %.1f iters/sec - remaining %s '''%(i+1, N, 100*i/N, fps, remaining_time)
#             sys.stdout.write(sent)
#             # sys.stdout.write("\r" + name + ''' | %s | %d/%d (%.1f percent) finished | %.1f iters/sec | remaining %s '''%(time_str, i+1, N, 100*i/N, fps, remaining_time))
#             sys.stdout.flush()
#     sent = '''\r''' + gettime(color=bcolors.OKCYAN) + " " +  '''%d/%d (%.1f percent) finished - %.1f iters/sec - remaining %s '''%(N, N, 100, fps, remaining_time)
#     # sys.stdout.write("\r" + name + ''' | %s | %d/%d (%.1f percent) finished | %.1f iters/sec | remaining %s '''%(time_str, N, N, 100, fps, remaining_time))
#     sys.stdout.write(sent)
#     sys.stdout.flush()
#     print("")

# class CustomLogger():
#     def d

# def remove_nonascii(text):
#     return ''.join([i if ord(i) < 128 else ' ' for i in text])

# class Performance():
#     def __init__(self, name):
#         self.name = name
#         d = datetime.datetime.now()
#         dstr = d.strftime('%Y-%m-%d %H:%M:%S')
#         print(bcolors.WARNING + dstr + bcolors.ENDC + " " + name.replace("+", "-"))
#         self.start = time.time()
#
#     def end(self):
#         self.end = time.time()
#         total = self.end - self.start
#         self.exetime = total
#         if total < 1e-6:
#             unit = 1e9
#             label = "nsec"
#         elif total < 10e-3:
#             unit = 1e6
#             label = "usec"
#         elif total < 10:
#             unit = 1e3
#             label = "msec"
#         else:
#             unit = 1.0
#             label = "sec"
#         d = datetime.datetime.now()
#         dstr = d.strftime('%Y-%m-%d %H:%M:%S')
#         print(bcolors.WARNING + dstr + bcolors.ENDC + " " + "{} ({} {})".format(self.name, int(total*unit), label))

# class AveragePerformance():
#     def __init__(self, name):
#         self.name = name
#         self.exetimes = []
#
#     def lapstart(self):
#         self.starttime = time.time()
#
#     def lapend(self):
#         self.endtime = time.time()
#         self.exetimes += [self.endtime - self.starttime]
#
#     def end(self):
#         unitlabels = {"ave":{"unit":None, "label":None, "val":np.mean(self.exetimes)},
#                      "sum":{"unit":None, "label":None, "val":np.sum(self.exetimes)}}
#         for ul in unitlabels:
#             if unitlabels[ul]["val"] < 1e-6:
#                 unitlabels[ul]["unit"] = 1e9
#                 unitlabels[ul]["label"] = "nsec"
#             elif unitlabels[ul]["val"] < 10e-3:
#                 unitlabels[ul]["unit"] = 1e6
#                 unitlabels[ul]["label"] = "usec"
#             elif unitlabels[ul]["val"] < 10:
#                 unitlabels[ul]["unit"] = 1e3
#                 unitlabels[ul]["label"] = "msec"
#             else:
#                 unitlabels[ul]["unit"] = 1.0
#                 unitlabels[ul]["label"] = "sec"
#         print("{} (average {} {}, total {} {})".format(self.name,
#               int(unitlabels["ave"]["val"]*unitlabels["ave"]["unit"]), unitlabels["ave"]["label"],
#               int(unitlabels["sum"]["val"]*unitlabels["sum"]["unit"]), unitlabels["sum"]["label"]))

# class Logger():
#     INFO = "INFO"
#     def __init__(basename):
#         self.basename = basename
#
#     def log(str, level):

# class bcolors:
#     HEADER = '\033[95m'
#     OKBLUE = '\033[94m'
#     OKCYAN = '\033[96m'
#     OKGREEN = '\033[92m'
#     WARNING = '\033[93m'
#     FAIL = '\033[91m'
#     ENDC = '\033[0m'
#     BOLD = '\033[1m'
#     UNDERLINE = '\033[4m'

def timelog(str):
    d = datetime.datetime.now()
    dstr = d.strftime('%Y-%m-%d %H:%M:%S')
    print(bcolors.WARNING + dstr + bcolors.ENDC + " " + str)
    # print(d.strftime('%Y-%m-%d %H:%M:%S'))

def gettime(colored=True, color=None):
    d = datetime.datetime.now()
    dstr = d.strftime('%Y-%m-%d %H:%M:%S')
    if color == None:
        return bcolors.WARNING + dstr + bcolors.ENDC
    else:
        return color + dstr + bcolors.ENDC

def forEach(vars):
    return zip(vars, range(len(vars)))

def secureListJoin(vars):
    if vars == None: return None
    if isinstance(vars, list):
        if len(vars) == 0: return None
        res = ""
        for v in vars:
            res += str(v) + ","
        res = res[:-1]
        return res
    else:
        return None

def secureLength(vars):
    # if vars == None: return 0
    if isinstance(vars, str):
        return len(vars)
    else:
        return 0


def removeAllFiles(dir, extension):
    for f in os.listdir(dir):
        if f.endswith(extension):
            os.remove(os.path.join(dir, f))

def relativeImportance(x, xe, ye):
    if isinstance(x, list):
        x = np.array(x)
    r = np.log(ye)/xe
    return np.exp(r*x)

def empty2None(vals):
    for v, index in su.forEach(vals):
        if isempty(vals[index]):
            vals[index] = None
    return vals


def datematchIndex(dates, targetdate, maxalloweddiff=5):
    # if isinstance(targetdate)
    mindiff = 1e9
    minindex = None
    for d, index in forEach(dates):
        diff = np.abs((targetdate - d).days)
        if (diff < mindiff)and(diff <= maxalloweddiff):
            mindiff = diff
            minindex = index
    return minindex


def makefolder(name):
    if not os.path.exists(name):
        os.makedirs(name)
    return name


def castDate(date):
    QUARTERS = {"Q1":"03-31", "Q2":"06-30", "Q3":"09-30", "Q4":"12-31"}
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    y = date.year
    m = date.month
    d = date.day
    if m in [1, 2, 3]:
        # return datetime.datetime.strptime("%d-03-31"%(y), "%Y-%m-%d")
        return datetime.datetime.strptime("{y}-{Q}".format(y=y, Q=QUARTERS["Q1"]), "%Y-%m-%d")
    if m in [4, 5, 6]:
        # return datetime.datetime.strptime("%d-06-30"%(y), "%Y-%m-%d")
        return datetime.datetime.strptime("{y}-{Q}".format(y=y, Q=QUARTERS["Q2"]), "%Y-%m-%d")
    if m in [7, 8, 9]:
        # return datetime.datetime.strptime("%d-09-30"%(y), "%Y-%m-%d")
        return datetime.datetime.strptime("{y}-{Q}".format(y=y, Q=QUARTERS["Q3"]), "%Y-%m-%d")
    if m in [10, 11, 12]:
        # return datetime.datetime.strptime("%d-12-31"%(y), "%Y-%m-%d")
        return datetime.datetime.strptime("{y}-{Q}".format(y=y, Q=QUARTERS["Q4"]), "%Y-%m-%d")


def securediv(n, d, errorval=None):
    if (n==None)or(d==None)or(n=="NULL")or(d=="NULL"): return errorval
    try: return n/d
    except ZeroDivisionError: return errorval


def removeDuplicate(vals, keys):
    '''
    vals: a list of lists
    keys: a list of keys (indices)
    '''
    res = []
    for i in range(len(vals)):
        hasduplicate = False
        for j in range(len(vals)):
            if i == j: continue
            rowduplicate = True
            for k in keys:
                if vals[i][k] != vals[j][k]:
                    rowduplicate = False
            if rowduplicate:
                hasduplicate = True
                break
        if not hasduplicate:
            res += [vals[i]]
    return res
    # for r, i in forEach(vals):

        # for rr, j in

def movingaverage(interval, window_size):
    window= np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')

def bidirectionalOperation(func, val):
    if val < 0:
        return -1*func(-1*val)
    else:
        return func(val)

# class ConfigManager():
#     def __init__(self, filepath, section="MAIN"):
#         self.orgconfigs = configparser.ConfigParser()
#         self.orgconfigs.readfp(open(filepath))
#         self.configs = {}
#         self.section = section
#
#     def getbool(self, name):
#         if self.orgconfigs[self.section][name] == "1":
#             return True
#         if self.orgconfigs[self.section][name] == "0":
#             return False
#
#     def getfloat(self, name):
#         return float(self.orgconfigs[self.section][name])
#
#     def getint(self, name):
#         return int(self.orgconfigs[self.section][name])
#
#     def getstr(self, name):
#         return self.orgconfigs[self.section][name]


def dtime2fyear(dtime):
    # if isinstance(dtime, list):
    #     res = []
    #     for i in range(len(dtime)):
    #         res += [dtime2fyear(dtime[i])]
    #     return res
    # if isinstance(dtime, pd.core.series.Series):
    #     return dtime2fyear(dtime.to_list())
    if isArrayLike(dtime):
        dtime = arraylikeToList(dtime)
        res = []
        for i in range(len(dtime)):
            res += [dtime2fyear(dtime[i])]
        return res
    else:
        if isempty(dtime): return np.nan
        # M2D = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
        M2D = {1:0, 2:31, 3:31+28, 4:31+28+31, 5:31+28+31+30, 6:31+28+31+30+30,
               7:31+28+31+30+30+30, 8:31+28+31+30+30+30+31, 9:31+28+31+30+30+30+31+31,
               10:31+28+31+30+30+30+31+31+30, 11:31+28+31+30+30+30+31+31+30+31,
               12:31+28+31+30+30+30+31+31+30+31+30}
        return dtime.year + (M2D[dtime.month]+ dtime.day)/365

def datetimeToFloatyear(dtime): # alias
    if isArrayLike(dtime):
        return dtime2fyear(dtime) # list
    else:
        return dtime2fyear(dtime)

def dictSwitchKeysItems(d):
    new_dict = {}
    for k, v in d.items():
        new_dict[v] = k
    return new_dict

# def quarters2YM(quarters):
#     # months = 4*quarters
#     y = int(quarters/4)
#     m = int((quarters - 4*y)*4)
#     return y, m

def shiftQuarters(dtime, quarters):
    '''
    expect dtime to be a standard quarter.
    quarters could be negative
    '''
    y = int(quarters/4)
    q = quarters - 4*y
    # print("y={}, q={}".format(y, q))
    stdq_str = dtime.strftime("%m-%d")
    # print("stdq_str=", stdq_str)
    STANDARD_QUARTERS = {"03-31":0, "06-30":1, "09-30":2, "12-31":3}
    if stdq_str not in STANDARD_QUARTERS.keys():
        return None
    stdq = int((STANDARD_QUARTERS[stdq_str] + q)%4)
    if stdq < 0 : stdq += 4
    # print("stdq=", stdq)
    Y = dtime.year + y
    Q = dictSwitchKeysItems(STANDARD_QUARTERS)[stdq]
    YYYY_MM_DD = "{}-{}".format(Y, Q)
    return str2dtime(YYYY_MM_DD)


def formatTextWidth(text, width):
    return "\n".join(wrap(text, width))

def frenchToEnglish(text):
    translationTable = str.maketrans("éàèùâêîôûç", "eaeuaeiouc")
    return text.translate(translationTable)

def latinToEnglish(text):
    return ''.join(char for char in
                   unicodedata.normalize('NFKD', text)
                   if unicodedata.category(char) != 'Mn')

def rowToCol(arr):
    if isinstance(arr, list):
        arr = np.array(arr)
    return arr[::,None]

def RMSError(arr1, arr2, relative=False, delta=0, r=2):
    arr1 = np.array(arr1)
    arr2 = np.array(arr2)
    if r <=0:
        raise Exception("r must be positive")
    if len(arr1) != len(arr2):
        raise Exception("length of arrays must be the same")
    error = arr1 - arr2
    if relative:
        error /= np.sqrt(arr1**2+arr2**2+delta)
    error = (np.sum(error**r)/len(error))**(1./r)
    return error


def timeseriesLinearRegression(timeseries, values):
    '''
    timeseries must be a list of datetime objects
    '''
    # X = np.array(timeseries)
    X = arraylikeToList(timeseries)
    if isinstance(X[0], str):
        X = stringToDatetime(X)
    X = datetimeToFloatyear(X)
    X = np.array(X)
    X -= X[0]
    X = X[::,None]
    y = values
    y = y.values
    y = y[::,None]
    reg = LinearRegression().fit(X, y)
    fittedline = reg.coef_[0][0]*X + reg.intercept_[0]
    fittedline = fittedline.flatten()
    return [reg.coef_[0][0], reg.intercept_[0], timeseries, fittedline]
