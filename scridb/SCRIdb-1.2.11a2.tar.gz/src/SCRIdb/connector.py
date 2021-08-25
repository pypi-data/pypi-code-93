#!/usr/bin/env python3

"""initiate connection to database
"""
import json
import os

import mysql.connector
from mysql.connector import errorcode


class Conn:
    def __init__(self):
        self.db = None
        self.cur = None
        self.config = None

    def conn(self, config: str = None):

        self.config = config

        if isinstance(config, dict):
            login = config
        elif os.path.isfile(config):
            login = json.load(open(config))
        else:
            login = None
        if login:
            try:
                self.db = mysql.connector.connect(
                    host=login["host"],
                    user=login["user"],
                    password=login["password"],
                    database=login["database"],
                )
                self.cur = self.db.cursor()
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)
