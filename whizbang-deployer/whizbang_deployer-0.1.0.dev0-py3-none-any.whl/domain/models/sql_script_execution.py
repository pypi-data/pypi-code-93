class SqlExecution:
    def __init__(self, database_execution_objects: 'list[DatabaseExecution]' = None):
        self.database_execution_objects = database_execution_objects or []


class DatabaseExecution:
    def __init__(self, database: str, scripts: 'list[str]' = None):
        self.database = database
        self.scripts = scripts or []