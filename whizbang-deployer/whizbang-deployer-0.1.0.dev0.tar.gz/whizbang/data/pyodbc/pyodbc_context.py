import pyodbc


class PyodbcContext:
    def __init__(self, server, database, username, password):
        self._connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password,
        autocommit=True)


    def execute_statements(self, statements: 'list[str]'):
        cursor = self._connection.cursor()
        results = []
        for statement in statements:

            try:
                result = cursor.execute(statement)
                print(results)
                results.append(result)
            except Exception as ex:
                print(f'sql_server statement error: {ex}')

        return results
