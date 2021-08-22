import sqlite3


class Insert:
    def __init__(self, table_name, db_path):
        self.table_name = table_name
        self.db_path = db_path
        self.get_columns()

    def get_columns(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"PRAGMA table_info({self.table_name});")
        table_data = c.fetchall()
        self.columns = []
        for column in table_data:
            self.columns.append(column[1])

    def add(self, **kwargs):
        add_to_columns = ""
        params_str = ""
        params = []
        for column in kwargs:
            add_to_columns += column + ', '
            params_str += "?, "
            params.append(kwargs[column])
        add_to_columns = add_to_columns[:len(add_to_columns) - 2]
        params_str = params_str[:len(params_str) - 2]
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"INSERT INTO {self.table_name} ({add_to_columns}) VALUES ({params_str})", tuple(params))
        conn.commit()
