from facata.utils import Connection, to_pyformat


class MariadbMariadbConnection(Connection):
    def run(self, sql, **params):
        self.cur.execute(to_pyformat(sql), params)
        return None if self.cur.description is None else self.cur.fetchall()

    @property
    def notifications(self):
        return []

    @property
    def parameter_statuses(self):
        return []


def connect(dbname, username, password, host, port, params):
    import mariadb

    for param, paramname in ((dbname, "database"), (port, "port")):
        if param is not None:
            params[paramname] = param

        if "autocommit" not in params:
            params["autocommit"] = True

    c = mariadb.connect(host=host, user=username, password=password, **params)
    return MariadbMariadbConnection(c)
