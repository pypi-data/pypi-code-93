from typing import List, overload


class UnileverAuth:
    integratorToken: str
    clientToken: str

    def __init__(self, integratorToken: str, clientToken: str):
        self.integratorToken = integratorToken
        self.clientToken = clientToken
