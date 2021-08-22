from .columns import (PrimaryKeyColumn, ForeignKeyColumn,
                      StringColumn, IntegerColumn,
                      FloatColumn, BooleanColumn)
import sqlite3
from . import querys


class Model:
    PrimaryKeyColumn = PrimaryKeyColumn
    ForeignKeyColumn = ForeignKeyColumn
    StringColumn = StringColumn
    IntegerColumn = IntegerColumn
    FloatColumn = FloatColumn
    BooleanColumn = BooleanColumn

    def __init__(self, name):
        self.name = name


class ModelFunc:
    def primary_key(self):
        for var in dir(self):
            if '__' in var:
                pass
            else:
                try:
                    if getattr(self, var).pk:
                        return var
                except:
                    pass

    def get_column(self):
        self.columns = {}
        for var in dir(self):
            if '__' not in var:
                class_in = getattr(self, var)
                if isinstance(class_in, (PrimaryKeyColumn, ForeignKeyColumn, IntegerColumn, StringColumn, FloatColumn, BooleanColumn)):
                    self.columns[var] = class_in
                    self.columns[var].name = var

    def check_for_changes(self):
        self.get_column(self)
        self.changes = []
        # check if table exists
        conn = sqlite3.connect(self.db_path, timeout=3)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name = ?;", (self.model.name,))
        table_data = c.fetchone()
        if table_data:
            # check for the if the columns exist
            c.execute(f"PRAGMA table_info({self.model.name});")
            column_in_db = c.fetchall()
            column_in_db_name = []
            for column in column_in_db:
                column_in_db_name.append(column[1])
            column_name = []
            for column in self.columns:
                column_name.append(column)
            if sorted(column_in_db_name) == sorted(column_name):
                pass
            else:
                column_name_test = column_name
                columns_names_in_db_test = column_in_db_name
                for column in column_name:
                    if column in column_in_db_name:
                        column_name_test.remove(column)
                        columns_names_in_db_test.remove(column)
                if column_name_test != []:
                    for column in column_name_test:
                        self.changes.append(f"Add column {column}")
                elif columns_names_in_db_test != []:
                    for column in columns_names_in_db_test:
                        self.changes.append(f"Remove column {column}")
            c.execute(f"PRAGMA table_info({self.model.name});")
            table_info = c.fetchall()
            for column in table_info:
                if column[1] in column_name:
                    if self.columns[column[1]].type != column[2]:
                        self.changes.append(f"'{column[1]}' is meant to be a {self.columns[column[1]].type} not a {column[2]}")
                    if self.columns[column[1]].pk != column[5]:
                        if column[5] == 1:
                            self.changes.append(f"'{column[1]}' is not meant to be a  pk.")
                        elif column[5] == 0:
                            self.changes.append(f"'{column[1]}' is meant to be a  pk.")
                    if self.columns[column[1]].not_null != column[3]:
                        if column[3] == 1:
                            self.changes.append(f"'{column[1]}' is not meant to be not null.")
                        elif column[3] == 0:
                            self.changes.append(f"'{column[1]}' is meant to be not null.")
                    if self.columns[column[1]].default != column[4]:
                        if f"[{self.columns[column[1]].default}]" != column[4]:
                            if self.columns[column[1]].default:
                                if str(self.columns[column[1]].default) != column[4]:
                                    self.changes.append(f"'{column[1]}'s default is meant to be {self.columns[column[1]].default} type {type(self.columns[column[1]].default)} not {column[4]} type {type(column[4])}")
                    c.execute(f"PRAGMA index_list({self.model.name});")
                    indexs = c.fetchall()
                    for index in indexs:
                        c.execute(f"PRAGMA index_info({index[1]});")
                        column_data = c.fetchone()
                        if column_data[2] == column[1]:
                            if not column_data and self.columns[column[1]].unique == 1:
                                self.changes.append(f"'{column[1]}' is meant to be unique.")
                            elif column_data and self.columns[column[1]].unique != 1:
                                self.changes.append(f"'{column[1]}' is not meant to be unique.")
                    c.execute(f"SELECT * FROM pragma_foreign_key_list('{self.model.name}')")
                    fk_data = c.fetchall()
                    for fk in fk_data:
                        if fk[3] == column[1]:
                            if not self.columns[column[1]].fk:
                                self.changes.append(f"'{column[1]}' is a fk when it should not be.")
                            else:
                                self.columns[column[1]].foreign_model.get_column(self.columns[column[1]].foreign_model)
                                if fk[2] != self.columns[column[1]].foreign_model.model.name:
                                    self.changes.append(f"'{column[1]}' is not linked to correct table.")
                                if self.columns[column[1]].foreign_model.primary_key(self.columns[column[1]].foreign_model) != fk[4]:
                                    self.changes.append(f"'{column[1]}' is not linked to correct column.")
                                if fk[6] != self.columns[column[1]].on_delete.sql:
                                    self.changes.append(f"'{column[1]}' on delete is not correct.")

        else:
            self.changes.append(f"Table '{self.model.name}' does not exist.")

        if self.changes != []:
            print(f"{len(self.changes)} unmigrated change(s):")
            for change in self.changes:
                print(f"- {change}")
        return self.changes

    def generate_migrations(self):
        self.get_column(self)
        table_creation_str = f"CREATE TABLE {self.model.name} ({self.columns[self.primary_key(self)].generate_sql()}, "

        for column in self.columns:
            if self.columns[column].pk is False:
                table_creation_str += self.columns[column].generate_sql() + ", "
        if table_creation_str[len(table_creation_str) - 2] == ',' and table_creation_str[len(table_creation_str) - 1] == ' ':
            table_creation_list = list(table_creation_str)
            table_creation_list[len(table_creation_str) - 2] = ')'
            table_creation_str = ""
            for char in table_creation_list:
                table_creation_str += char
        else:
            print(table_creation_str[len(table_creation_str) - 2])
            table_creation_str += ")"

        migration_str = f"""\n
class {self.model.name}(Migration):
    def __init__(self):
        self.table_name = "{self.model.name}"
        self.table_creation_str = "{table_creation_str}"
        self.changes = {self.changes}
        self.columns = {list(self.columns.keys())}"""
        return migration_str

    def load_querrys(self):
        self.select = querys.select.Get(self.model.name, self.db_path)
        self.insert = querys.insert.Insert(self.model.name, self.db_path)
        self.delete = querys.delete.Delete(self.model.name, self.db_path)
        self.update = querys.update.Update(self.model.name, self.db_path)
