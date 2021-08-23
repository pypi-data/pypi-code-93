from typing import Optional


class User:

    def __init__(self, 
                names: str, 
                lastNames: str,
                email: str, 
                password: Optional[bytes] = None,
                id: Optional[int] = None):
        self.Id = id
        self.Name = names
        self.LastName = lastNames
        self.Email = email
        self.Password = password
