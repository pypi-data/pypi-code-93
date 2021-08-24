class Query:
    """Container for the data that makes up a query request to Luminesce

    """

    def __init__(self, sql_str: str, name: str = None, timeout: int = 3600*3, keep_for: int = 3600*6):
        """__init__ method for the query container class

        Args:
            sql_str (str): the SQL query to be executed.
            name (str): the name of the query. Defaults to 'Query'.
            timeout (int): query timeout time in seconds. Defaults to 7200s (2hrs).
            keep_for (int): keep data for time in seconds. Defaults to 3600s (1hr).
        """
        if not isinstance(sql_str, str):
            raise TypeError(f"Input to sql arg of the ctor should be a str but was {type(sql_str).__name__}")
        if len(sql_str) == 0:
            raise ValueError(f"Input SQL string was empty.")
        if not isinstance(name, str) and name is not None:
            raise TypeError(f"Input to name arg of the ctor should be a str but was {type(name).__name__}")
        if not isinstance(timeout, int):
            raise TypeError(f"Input to timeout arg of the ctor should be a int but was {type(timeout).__name__}")
        if not isinstance(keep_for, int):
            raise TypeError(f"Input to keep_for arg of the ctor should be a int but was {type(keep_for).__name__}")

        self.sql_str = sql_str
        self.params = {
            "queryName": "Query" if name is None else name,
            "timeoutSeconds": str(timeout),
            "keepForSeconds": str(keep_for)
        }
