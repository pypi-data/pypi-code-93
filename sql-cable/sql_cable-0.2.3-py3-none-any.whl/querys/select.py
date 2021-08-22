import sqlite3


def get_data(db_path, querys, fetch, params=None):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    if params:
        c.execute(querys, tuple(params))
    else:
        c.execute(querys)
    if fetch == 'all':
        result = c.fetchall()
    else:
        result = c.fetchone()
    return result


class RowObject:
    def __init__(self, row_data, columns):
        self.row_data = row_data
        self.columns = columns
        self.row_to_var()

    def row_to_var(self):
        for i in range(len(self.columns)):
            exec(f"self.{self.columns[i]} = value", {'self': self, 'value': self.row_data[i]})


class f_funcs:
    def __init__(self, table_name, db_path, columns, query, params):
        self.table_name = table_name
        self.db_path = db_path
        self.columns = columns
        self.query = query
        self.params = params

    def all(self):
        result = get_data(self.db_path, self.query, 'all', params=self.params)
        f_result = []
        if result != []:
            for row in result:
                f_result.append(RowObject(row, self.columns))
            return f_result

    def one(self):
        result = get_data(self.db_path, self.query, 'one', params=self.params)
        if result:
            return RowObject(result, self.columns)


class Sort_by(f_funcs):
    def __init__(self, table_name, db_path, columns, query, params):
        self.table_name = table_name
        self.db_path = db_path
        self.columns = columns
        self.query = query
        self.params = params

    def sort_by(self, column, mode):
        self.query += f"ORDER BY {column}, {mode}"
        return f_funcs(self.table_name, self.db_path, self.columns, self.query, self.params)


class Filter:
    def __init__(self, table_name, db_path, columns, query, params):
        self.table_name = table_name
        self.db_path = db_path
        self.columns = columns
        self.query = query
        self.params = params

    def filter(self, **kwargs):
        self.query += " WHERE "
        self.params = []
        for param in kwargs:
            self.query += f"{param} = ?"
            self.params.append(kwargs[param])
        return Sort_by(self.table_name, self.db_path, self.columns, self.query, self.params)


class Get(f_funcs):
    def __init__(self, table_name, db_path):
        self.table_name = table_name
        self.db_path = db_path
        self.get_columns()
        self.query = f"SELECT * FROM {self.table_name}"
        self.params = []
        self.filter = Filter(self.table_name, self.db_path, self.columns, self.query, self.params).filter
        self.sort_by = Sort_by(self.table_name, self.db_path, self.columns, self.query, self.params).sort_by

    def get_columns(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"PRAGMA table_info({self.table_name});")
        table_data = c.fetchall()
        self.columns = []
        for column in table_data:
            self.columns.append(column[1])
