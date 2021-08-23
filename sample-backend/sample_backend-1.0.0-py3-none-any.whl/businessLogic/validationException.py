
from typing import Optional


class ValidationException(Exception):
    
    def __init__(self, *args: object, field: Optional[str] == None, ) -> None:
        super().__init__(*args)
        self.Field = field
