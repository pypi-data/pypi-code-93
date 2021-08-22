import sqlite3


class Migration:
    def update(self, db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute(f"PRAGMA table_info({self.table_name});")
        column_in_db = c.fetchall()

        existing_column_str = ""
        existing_column_args_str = ""

        for column in self.columns:
            for column_in in column_in_db:
                if column == column_in[1]:
                    existing_column_args_str += "?,"
                    removed = False
                    for change in self.changes:
                        if change == f'Remove column {column[1]}':
                            removed = True
                    if not removed:
                        existing_column_str += column_in[1] + ", "
                    break

        existing_column_str = existing_column_str[:len(existing_column_str) - 2]
        existing_column_args_str[:len(existing_column_args_str) - 2]
        # get table data
        c.execute(f"SELECT {existing_column_str} FROM {self.table_name}")
        self.table_data = c.fetchall()

        c.execute(f"DROP TABLE {self.table_name}")
        conn.commit()
        c.execute(self.table_creation_str)
        conn.commit()

        for row in self.table_data:
            args = []
            for i in range(len(row)):
                args.append(row[i])
            c.execute(f"INSERT INTO ({existing_column_str}) VALUES({existing_column_args_str})", tuple(args))

    def create(self, db_path):
        conn = sqlite3.connect(db_path, timeout=3)
        c = conn.cursor()
        c.execute(self.table_creation_str)
        conn.commit()

    def run_migration(self, db_path):
        if f"Table '{self.table_name}' does not exist." in self.changes:
            self.create(db_path)
        else:
            self.update(db_path)
