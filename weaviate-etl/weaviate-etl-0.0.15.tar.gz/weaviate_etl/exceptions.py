"""
Weaviate ETL Exceptions.
"""


class UnableToGetWeaviateClient(Exception):
    """
    Unable to connect to Weaviate client
    """


class NoInstanceLoaded(Exception):
    """
    Unable to connect to Weaviate client
    """

class NoModelLoaded(Exception):
    """
    Unable to connect to Weaviate client
    """


class DuplicateClassInSchema(Exception):
    """
    Duplicate class in schema exception
    """
    def __init__(self, message: str):
        Exception.__init__(self, "Duplicate class in schema:" + message)
        self.message = message


class UnableToCreateSchema(Exception):
    """
    Unable to create schema exception
    """


class UnableToLoadSchema(Exception):
    """
    Unable to load schema exception
    """


class UnableToOpenModelFile(Exception):
    """
    Unable to open model file exception
    """


class UnsupportedModelType(Exception):
    """
    Model type is not supported yet
    """
    def __init__(self, message: str):
        Exception.__init__(self, "Modeltype not supported yet:" + message)
        self.message = message


class UnknownModelType(Exception):
    """
    Unknow model type
    """


class NoClassificationSet(Exception):
    """
    No classification specified in model
    """
