from databases import Database


class SQLEngine:
    def __init__(self, connection: Database) -> None:
        """For SQL database engines.

        postgresql, mysql, & sqlite supported.

        Parameters
        ----------
        connection : Database
        """

        self._connection = connection


class MongoEngine:
    def __init__(self, host: str = "localhost",
                 port: int = 27017, database: str = "aioaccount"
                 ) -> None:
        """For mongodb engine.

        Parameters
        ----------
        host : str, optional
            by default "localhost"
        port : int, optional
            by default 27017
        """

        self._connection = f"mongodb://{host}:{port}"
        self._database = database
