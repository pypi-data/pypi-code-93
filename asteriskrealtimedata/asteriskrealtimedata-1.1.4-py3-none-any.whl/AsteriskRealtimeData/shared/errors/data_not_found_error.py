class DataNotFound(Exception):
    def __init__(self, table_name: str, search_criteria: dict, message: str = "Data not found"):
        self.table_name = table_name
        self.search_criteria = search_criteria
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"Data not found in {self.table_name} using search criteria: {str(self.search_criteria)}"
