# -*- coding=utf-8 -*-

import pyodbc

from x_py_libs.db import BaseDBHelper

class MSSQLDBHelper(BaseDBHelper):
  

    def connect(self):
        try:
            conn = pyodbc.connect(self.connect_string)
            return conn
        except Exception:
            print('mssql error')
            raise

    def fetch_returning_id(self, sql, *params):
        def callback(cur):
            return cur.fetchone()[0]

        return self.execute_sql(sql, callback, *params)

    # def fetch_rowcount(self, sql, *params):
    #     def callback(cur):
    #         return cur.rowcount

    #     return self.execute_sql(sql, callback, *params)

    # def fetch_one(self, sql, *params):
    #     def callback(cur):
    #         return cur.fetchone()

    #     return self.execute_sql(sql, callback, *params)

    # def fetch_all(self, sql, *params):
    #     def callback(cur):
    #         return cur.fetchall()

    #     return self.execute_sql(sql, callback, *params)

    def execute_sql(self, sql, callback, *params):
        conn = self.connect()

        if conn == None:
            return None

        cur = conn.cursor()

        # print('mssql:', sql, params)
        cur.execute(sql, params)

        # columns = [column[0] for column in cursor.description]
        # for row in cursor.fetchall():
        #     x = dict(zip(columns, row))
        #     results.append(x)

        rst = callback(cur)
        conn.commit()
        conn.close()
        return rst


"""
cursor = cnxn.cursor()

print ('Inserting a new row into table')
#Insert Query
tsql = "INSERT INTO Employees (Name, Location) VALUES (?,?);"
with cursor.execute(tsql,'Jake','United States'):
    print ('Successfuly Inserted!')


#Update Query
print ('Updating Location for Nikita')
tsql = "UPDATE Employees SET Location = ? WHERE Name = ?"
with cursor.execute(tsql,'Sweden','Nikita'):
    print ('Successfuly Updated!')


#Delete Query
print ('Deleting user Jared')
tsql = "DELETE FROM Employees WHERE Name = ?"
with cursor.execute(tsql,'Jared'):
    print ('Successfuly Deleted!')


#Select Query
print ('Reading data from table')
tsql = "SELECT Name, Location FROM Employees;"
with cursor.execute(tsql):
    row = cursor.fetchone()
    while row:
        print (str(row[0]) + " " + str(row[1]))
        row = cursor.fetchone()
"""
