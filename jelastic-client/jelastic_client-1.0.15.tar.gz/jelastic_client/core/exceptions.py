from typing import Dict


class JelasticClientException(Exception):
    """
    Generic Jelastic Client Exception
    """

    def __init__(self, message: str, response: Dict):
        super().__init__(message)
        self.response = response


class ApiClientException(JelasticClientException):
    """
    Low-level API Exception
    """

    def __init__(self, message: str, response: Dict):
        super().__init__(message, response)
